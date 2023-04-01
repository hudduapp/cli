import json

import requests


class ApiClient:
    def __init__(self, base_url: str, headers: dict = {}):
        self.base_url = base_url
        self.headers = headers

    def request(
            self, method: str, path: str, body: dict = None, params: dict = None
    ) -> dict:
        
        res = requests.request(
            method,
            f"{self.base_url}/{path}",
            headers=self.headers if self.headers else {},
            data=json.dumps(body) if not method == "GET" else None,
            params=params,
        )

        try:
            return res.json()
        except:
            raise Exception(res.text)
