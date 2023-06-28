import logging
import time
import requests
import fastapi as _fastapi
from aiohttp import ClientSession

from backend.core.config import settings

logging.basicConfig(**settings.LOGGING_STANDARD_PARAMS)
logger = logging.getLogger(__name__)


def vk_synchronous_request(url, params, **kwargs):
    """Perform a custom synchronous request to VK API."""

    while True:
        response = requests.get(url, params=params, timeout=60).json()

        if "error" not in response:
            return response

        error = response["error"]

        # Too many requests per second.
        if error["error_code"] == 6:
            logger.debug(error["error_msg"])
            time.sleep(0.1)
            continue

        # Critical errors.
        if error["error_code"] == 100:
            logger.info(error["error_msg"], params)
            detail = error["error_msg"]
            if "owner_id is undefined" in error["error_msg"] and "domain" in kwargs:
                detail = f"Человек/сообщество с адресом {kwargs['domain']} не найдены."
            raise _fastapi.HTTPException(status_code=404, detail=detail)

        # Some other unexpected critical errors.
        logger.error(error["error_msg"])
        raise _fastapi.HTTPException(status_code=500, detail=error["error_msg"])


async def vk_asynchronous_request(url, params, **kwargs):
    """Perform a custom asynchronous request to VK API."""

    async with ClientSession() as session:
        while True:
            async with session.get(url=url, params=params) as response:
                resp_json = await response.json()

                if "error" not in resp_json:
                    return resp_json

                error = resp_json["error"]

                # Too many requests per second.
                if error["error_code"] == 6:
                    logger.debug(error["error_msg"])
                    time.sleep(0.1)
                    continue

                # Critical errors.
                if error["error_code"] == 100:
                    logger.info(error["error_msg"], params)
                    detail = error["error_msg"]
                    if (
                        "owner_id is undefined" in error["error_msg"]
                        and "domain" in kwargs
                    ):
                        detail = (
                            f"Человек/сообщество с адресом "
                            f"{kwargs['domain']} не найдены."
                        )
                    raise _fastapi.HTTPException(status_code=404, detail=detail)

                # Some other unexpected critical errors.
                logger.error(error["error_msg"])
                raise _fastapi.HTTPException(status_code=500, detail=error["error_msg"])
