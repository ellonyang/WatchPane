from urllib.parse import urljoin

import requests

from settings import Settings
import schemas

setting = Settings()


class Api:
    def __init__(self):
        self.base_url = setting.api

    def url(self, path: str):
        print(self.base_url, path)
        return urljoin(self.base_url, path)

    def get_watches(self):
        url = self.url("/watches")
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def all(self):
        url = self.url("/watches/order")
        print(url)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def update_watch(self, watch_data):
        url = self.url("/watch/update")
        response = requests.post(url, json=schemas.WatchUpdateSchema(**watch_data).dict())
        response.raise_for_status()
        return response.json()
