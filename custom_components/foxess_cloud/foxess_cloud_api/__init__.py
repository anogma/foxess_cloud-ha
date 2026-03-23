"""FoxESS Cloud API client implementation."""

import hashlib
import time

import aiohttp

FOXESS_CLOUD_DOMAIN = "https://www.foxesscloud.com"


class FoxESSCloud:
    """FoxESS Cloud API client class."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession = None) -> None:
        """Initialize FoxESSCloud instance."""

        self.api_key = api_key
        if session is None:
            self.session = aiohttp.ClientSession()
        else:
            self.session = session

    def _get_signature(self, path: str, lang: str = "en") -> dict[str, str]:
        timestamp = round(time.time() * 1000)
        signature = rf"{path}\r\n{self.api_key}\r\n{timestamp}"
        return {
            "token": self.api_key,
            "lang": lang,
            "timestamp": str(timestamp),
            "signature": self._md5c(text=signature),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/117.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
        }

    def _md5c(self, text: str = "", _type: str = "lower") -> str:
        res = hashlib.md5(text.encode(encoding="UTF-8")).hexdigest()
        if _type == "lower":
            return res

        return res.upper()

    async def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        url = FOXESS_CLOUD_DOMAIN + path
        headers = self._get_signature(path)
        async with self.session.request(
            method=method, url=url, json=json, headers=headers, params=params
        ) as response:
            response.raise_for_status()
            if response.status != 200:
                raise FoxESSCloudException(
                    f"API request failed with status code {response.status}: {response.reason}"
                )
            json = await response.json()
            if json.get("errno") != 0:
                raise FoxESSCloudException(
                    "API request failed",
                    json.get("errno"),
                    json.get("msg"),
                    json.get("result"),
                )
            return json

    async def get_plants(self, currentPage=1, pageSize=10):
        """Get plant list (not used currently, but may be useful for future expansion)."""
        request_json = {"currentPage": currentPage, "pageSize": pageSize}
        response_json = await self._request(
            "post", "/op/v0/plant/list", json=request_json
        )
        return response_json.get("result")

    async def get_device_detail(self, device_sn: str):
        """Get device detail data."""
        params = {"sn": device_sn}
        json = await self._request("get", "/op/v1/device/detail", params=params)
        return json.get("result")

    async def get_device_variable(self):
        """Get device variable list (not used currently, but may be useful for future expansion)."""
        json = await self._request("get", "/op/v0/device/variable/get")
        return json.get("result")

    async def get_device_real_time_data(self, device_sn: str, variable_list: list[str]):
        """Get device real-time data for specified variables."""
        request_json = {"sns": [device_sn], "variableList": variable_list}
        json = await self._request(
            "post", "/op/v1/device/real/query", json=request_json
        )
        datas = json.get("result")[0].get("datas")
        result = {}
        for item in datas:
            value = item["value"]
            # Normalize to kWh
            if item.get("unit") is not None:
                unit = item["unit"]
                if unit == "0.1kWh":
                    value = value / 10
                elif unit == "0.01kWh":
                    value = value * 100
            result[item["variable"]] = value
        return result

    async def get_device_generation(self, device_sn: str):
        """Get device generation data."""
        params = {"sn": device_sn}
        json = await self._request("get", "/op/v0/device/generation", params=params)
        return json.get("result")

    def detect_pv_count(self, device_real_time_data: dict) -> int:
        """Detect PV count from real-time data."""
        count = 0
        for i in range(1, 25):
            if device_real_time_data.get(f"pv{i}Volt") is not None:
                count += 1
            else:
                break
        return count


class FoxESSCloudException(Exception):
    """Custom exception for FoxESSCloud errors."""
