import json
import sys

import requests


class ApiClient:
    def __init__(self, base_url: str, headers: dict = {}):
        self.base_url = base_url
        self.headers = headers

    def request(
        self, method: str, path: str, body: dict = None, params: dict = None
    ) -> dict:
        """
        This should handle errors fairly well
        :param method:
        :param path:
        :param body:
        :param params:
        :return:
        """
        res = requests.request(
            method,
            f"{self.base_url}/{path}",
            headers=self.headers if self.headers else {},
            data=json.dumps(body) if not method == "GET" else None,
            params=params,
        )

        if res.status_code < 300:
            return res.json()
        else:
            print("Something went wrong! Here are some clues:")
            try:
                print(res.json()["error"])
            except:
                print(res.text)
            sys.exit()
