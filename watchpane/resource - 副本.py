import asyncio
import contextlib
import datetime
import functools
import pathlib
import re
import time
from asyncio import Event
from typing import TypedDict
from urllib.parse import urljoin
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
    user_data_dir = pathlib.Path("play")
    if _browser_context is None:
        playwright = await async_playwright().start()
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir.absolute().as_posix(), headless=False
        )
        await context.new_page()

        _browser_context = {
            "playwright": playwright,
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
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)

    return wrapper


@contextlib.asynccontextmanager
async def context_page(context) -> Page:
    page = await context.new_page()
    try:
        yield page
    finally:
        await page.close()


@on_limit
async def run_watch(url, watch_data, context: BrowserContext):
    device_id = watch_data["url"]
    # async with new_page() as page:
    async with context_page(context) as page:
        retries = 0
        while retries < 2:
            retries += 1
            await page.goto(url)
            # <p class="max-w-[340px] text-center text-sm text-black dark:text-white">Cannot read properties of undefined (reading 'brand_name')</p>
            await page.wait_for_load_state("networkidle")
            if "Cannot read properties" in await page.content():
                await asyncio.sleep(20)
                if "Cannot read properties" in await page.content():
                    logger.error("页面加载失败: Cannot read properties")
                    update_watch(watch_data, state="uncheck")
                    return f"{url} 页面加载失败"
            device_content = await page.get_by_role("heading", name="Device ID:").inner_text()
            if device_id not in device_content:
                logger.error("device_id: {} not found in {}", device_id, device_content)
                continue
            text = await page.locator("div").filter(
                has=page.get_by_role("heading", name=re.compile("(Down|Up) For"))
            ).last.inner_text()
            text = text.lower()
            state = None
            if "running" in text:
                state = "running"
            if "failed" in text:
                state = "failed"

            print(f"{device_content}抓取到的文本:{text}")
            if state is None:
                logger.error("未知状态，请人工检查")
                continue
            update_watch(watch_data, state)
            return url


def update_watch(watch_data: dict, state: str):
    watch_data["status"] = state
    if state == "running":
        watch_data["last_success_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        watch_data["failed_count"] = 0
    else:
        watch_data["failed_count"] += 1
        watch_data["last_success_at"] = watch_data["last_check_at"].replace("T", " ") if watch_data["last_check_at"] else None
    watch_data["last_check_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time.sleep(5)
    print("更新状态:", watch_data)
    api = Api()
    new_watch = api.update_watch(watch_data)
    print("更新后的状态:", new_watch)


async def watch_pages():
    _stop.clear()
    async with async_playwright() as p:
        user_data_dir = pathlib.Path("play")
        context = await p.chromium.launch_persistent_context(
            user_data_dir.absolute().as_posix(), headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context.set_default_navigation_timeout(50 * 1000)
        context.set_default_timeout(50 * 1000)
        while not _stop.is_set():
            api = Api()
            tasks = []
            try:
                data = api.get_watches()
                if not data:
                    logger.debug("等待监控任务")
                    await asyncio.sleep(40)
                    continue
                async with asyncio.TaskGroup() as group:
                    for watch in data:
                        url = urljoin(setting.watch_url, watch["url"])
                        tasks.append(group.create_task(run_watch(url, watch, context)))
                for task in tasks:
                    print("完成", task.result())
                await asyncio.sleep(setting.check_interval * 10)
            except Exception as e:
                logger.exception(e)
                await asyncio.sleep(400)


if __name__ == '__main__':
    asyncio.run(watch_pages())
