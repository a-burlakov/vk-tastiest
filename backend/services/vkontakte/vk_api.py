import asyncio
import logging
import time
from dataclasses import dataclass

import requests
import aiohttp
import fastapi as _fastapi

from backend.core.config import settings

logging.basicConfig(**settings.LOGGING_STANDARD_PARAMS)
logger = logging.getLogger(__name__)
sem = asyncio.Semaphore(60)


def vk_synchronous_request(url: str, params: dict, **kwargs):
    """Perform a custom synchronous request to VK API."""

    while True:
        resp_json = requests.get(url, params=params, timeout=60).json()

        if "error" in resp_json:
            error = VKError(resp_json["error"], params=params | kwargs)
            error.handle_error_sync()
            continue

        return resp_json


async def vk_asynchronous_request(url: str, params: dict, **kwargs):
    """Perform a custom asynchronous request to VK API."""

    async with sem:
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(url=url, params=params) as response:
                    resp_json = await response.json()

                if "error" in resp_json:
                    error = VKError(
                        resp_json["error"],
                        params=params | kwargs,
                    )
                    await error.handle_error_async()
                    continue

                break

    return resp_json


@dataclass
class VKError:
    """Class for managing errors came from VK API."""

    # Error representation as it is from VK API as dict.
    error: dict
    # Custom request parameters that were in context at the request time.
    params: dict

    async def handle_error_async(self) -> None:
        """Check if the error is critical and raises an exception if it is."""

        # Too many requests per second.
        if self.error["error_code"] == 6:
            logger.debug(self.error["error_msg"])
            await asyncio.sleep(0)

            return

        self.handle_critical_error()

    def handle_error_sync(self) -> None:
        """Check if the error is critical and raises an exception if it is."""

        # Too many requests per second.
        if self.error["error_code"] == 6:
            logger.debug(self.error["error_msg"])
            time.sleep(0.1)
            return

        self.handle_critical_error()

    def handle_critical_error(self):
        """If the error is critical, raises an corresponding exception."""

        # Specific critical errors.
        if self.error["error_code"] == 100:
            logger.info(self.error["error_msg"], self.params)
            detail = self.error["error_msg"]
            if (
                "owner_id is undefined" in self.error["error_msg"]
                and "domain" in self.params
            ):
                detail = (
                    f"Человек/сообщество с адресом {self.params['domain']} не найдены."
                )
            raise _fastapi.HTTPException(status_code=404, detail=detail)

        # Unexpected critical errors.
        logger.error(self.error["error_msg"])
        raise _fastapi.HTTPException(status_code=500, detail=self.error["error_msg"])
