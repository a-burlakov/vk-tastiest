from dataclasses import dataclass
import requests
import fastapi as _fastapi
import aiohttp
import asyncio

from aiohttp import ClientSession

from backend.logger import logger
from backend.constants import VKAPI_TOKEN, VKAPI_VERSION, VKAPI_URL
from backend.vkscript import GET_POSTS_TEMPLATE


@dataclass
class PostFetcher:
    """
    Fetches posts from VK group or person.
    """

    domain: str  # Group or person address in VK, e.g. "a_a_burlakov"

    _total_posts: int = 0

    def _set_total_posts_in_domain(self) -> None:
        """Sets "_total_posts" as amount of posts in the VK domain."""
        logger.info(f'Getting total posts in "vk.com/{self.domain}"...')

        params = {
            "v": VKAPI_VERSION,
            "access_token": VKAPI_TOKEN,
            "count": 1,
            "domain": self.domain,
        }

        while True:
            response = requests.get(VKAPI_URL + "wall.get", params=params).json()
            if "error" in response:
                error = response["error"]

                # If too many requests per second, we'll just wait a bit.
                if error["error_code"] == 6:
                    logger.error(f'{error["error_msg"]}')
                    continue

                raise _fastapi.HTTPException(status_code=500, detail=error["error_msg"])

            break

        self._total_posts = response["response"]["count"]
        logger.info(f"Total posts in VK domain: {self._total_posts}")

    def fetch_posts_synchronously(self) -> list:
        """
        Fetches posts from VK domain synchronously.
        :return: a list of posts in the VK domain.
        """
        fetched_posts: list = []
        self._set_total_posts_in_domain()

        if not self._total_posts:
            return fetched_posts

        logger.info(f'Start fetching posts from "vk.com/{self.domain}"...')

        current_offset = 0
        while len(fetched_posts) < self._total_posts:
            vks_code = GET_POSTS_TEMPLATE.substitute(
                {"domain": self.domain, "offset": current_offset, "count": 100}
            )

            params = {"v": VKAPI_VERSION, "access_token": VKAPI_TOKEN, "code": vks_code}
            while True:
                response = requests.get(
                    VKAPI_URL + "execute",
                    params=params,
                    timeout=60,
                ).json()

                # If too many requests per second, we'll just wait a bit.
                if "error" in response:
                    error = response["error"]

                    if error["error_code"] == 6:
                        logger.error(f'{error["error_msg"]}')
                        continue

                    raise _fastapi.HTTPException(
                        status_code=500, detail=response["error"]["error_msg"]
                    )
                break

            fetched_posts.extend(response["response"]["items"])
            current_offset += 2500
            logger.info(f'Fetched {len(fetched_posts)}/{self._total_posts} posts"...')

        logger.info(f'End fetching posts from "vk.com/{self.domain}"...')
        return fetched_posts

    async def fetch_posts_for_offset(self, offset):
        logger.info(
            f'(offset {offset}) Start fetching posts from "vk.com/{self.domain}"...'
        )

        async with ClientSession() as session:
            vks_code = GET_POSTS_TEMPLATE.substitute(
                {
                    "domain": self.domain,
                    "offset": offset,
                    "count": 100,
                    "iterations": 10,
                }
            )
            params = {"v": VKAPI_VERSION, "access_token": VKAPI_TOKEN, "code": vks_code}
            url = VKAPI_URL + "execute"

            while True:
                async with session.get(url=url, params=params) as response:
                    resp_json = await response.json()

                    # If too many requests per second, we'll just wait a bit.
                    if "error" in resp_json:
                        error = resp_json["error"]

                        if error["error_code"] == 6:
                            logger.error(f'{error["error_msg"]}')
                            await asyncio.sleep(delay=1)
                            continue

                        raise _fastapi.HTTPException(
                            status_code=500, detail=resp_json["error"]["error_msg"]
                        )

                    logger.info(
                        f'(offset {offset}) End fetching posts from "vk.com/{self.domain}"...'
                    )

                    return resp_json["response"]["items"]

    async def fetch_posts_asynchronously(self) -> list:
        """
        Fetches posts from VK domain synchronously.
        :return: a list of posts in the VK domain.
        """
        fetched_posts: list = []
        self._set_total_posts_in_domain()

        if not self._total_posts:
            return fetched_posts

        tasks = []
        offsets = [o for o in range(0, self._total_posts, 1000)]
        for offset in offsets:
            tasks.append(asyncio.create_task(self.fetch_posts_for_offset(offset)))

        results = await asyncio.gather(*tasks)
        fetched_posts = [post for result in results for post in result]
        return fetched_posts
