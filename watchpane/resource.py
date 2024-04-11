import asyncio
import contextlib
import datetime
import functools
from asyncio import Event
from typing import TypedDict
from urllib.parse import urljoin

import requests
from loguru import logger
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page
from settings import Settings
from api import Api

setting = Settings()


class Context(TypedDict):
    playwright: Playwright
    browser: Browser
    context: BrowserContext


_browser_context: Context | None = None


async def get_context() -> Context:
    global _browser_context
    if _browser_context is None:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(channel="chrome", headless=False)
        context = await browser.new_context()
        _browser_context = {
            "playwright": playwright,
            "browser": browser,
            "context": context
        }
    return _browser_context


async def close_context():
    global _browser_context
    if _browser_context is not None:
        await _browser_context["browser"].close()
        await _browser_context["playwright"].stop()
        _browser_context = None


@contextlib.asynccontextmanager
async def new_page() -> Page:
    context = await get_context()
    page = await context["context"].new_page()
    try:
        yield page
    finally:
        await page.close()


_stop = Event()
limit = asyncio.Semaphore(setting.async_page)


def on_limit(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        async with limit:
            return await func(*args, **kwargs)

    return wrapper


@on_limit
async def run_watch(url, watch_data):
    device_id = watch_data["url"]
    async with new_page() as page:
        retries = 0
        while retries < 2:
            retries += 1
            await page.goto(url)
            device_content = await page.get_by_role("heading", name="Device ID:").inner_text()
            if device_id not in device_content:
                logger.error("device_id: {} not found in {}", device_id, device_content)
                continue
            text = await page.locator("div").filter(has_text="Up For").first.inner_text()
            if "running" in text:
                state = "RUNNING"
            else:
                state = "FAILED"
            update_watch()


def update_watch(watch_data: dict, state: str):
    watch_data["status"] = state
    if state == "RUNNING":
        watch_data["last_success_at"] = datetime.datetime.now()
        watch_data["failed_count"] = 0
    else:
        watch_data["failed_count"] += 1
    watch_data["last_check_at"] = datetime.datetime.now()

    api = Api()
    api.update_watch(watch_data)


async def watch_pages():
    _stop.clear()
    while not _stop.is_set():
        api = Api()
        tasks = []
        async with asyncio.TaskGroup() as group:
            for watch in api.get_watches():
                url = urljoin(setting.watch_url, watch["url"])
                tasks.append(group.create_task(run_watch(url, watch["url"])))
        for task in tasks:
            print("完成", task.result())
        await asyncio.sleep(10)

    await close_context()


if __name__ == '__main__':
    asyncio.run(watch_pages())
