from urllib.parse import urljoin

import requests

from settings import Settings

setting = Settings()


class Api:
    def __init__(self):
        self.base_url = setting.api

    def url(self, path: str):
        print(self.base_url, path)
        return urljoin(self.base_url, path)

    def get_watches(self):
        # url = self.url("/watches")
        # response = requests.get(url)
        # response.raise_for_status()
        # return response.json()
        return [
            {"url": "1"},
            {"url": "2"},
            {"url": "3"},
            {"url": "4"},
            {"url": "5"},

        ]

    def all(self):
        url = self.url("/watches/order")
        print(url)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_by_name(self, name: str):
        url = self.url("/watch/by_name")
        response = requests.get(url, params={"name": name})
        response.raise_for_status()
        return response.json()