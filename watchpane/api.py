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
        url = self.url("/watches/order")
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
        url = self.url("/update")
        data = schemas.WatchUpdateSchema(**watch_data).dict()
        response = requests.post(url, json=data)
        print("服务器文本:", response.text)
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    api = Api()
    print(api.all())
    print(api.get_watches())
    api.update_watch({
        "id": 1,
        "status": "RUNNING",
        "last_check_at": "2022-01-01 12:00:00",
        "last_success_at": None,
        "last_execute_at": None,
        "failed_count": 0
    })
    print(api.get_watches())
    print(api.all())
