import time
from dataclasses import dataclass
import asyncio
import requests
import fastapi as _fastapi
from aiohttp import ClientSession

from backend.logger import logger
from backend.constants import VKAPI_TOKEN, VKAPI_VERSION, VKAPI_URL
from backend.vkscript import GET_POSTS_TEMPLATE


@dataclass
class PostFetcher:
    """
    Fetches posts from VK group or person.
    """

    vk_domain: str  # Group or person address in VK, e.g. "a_a_burlakov"

    _url_wall_get = VKAPI_URL + "wall.get"
    _total_posts_in_domain: int = 0

    # Number of times to execute query via "/execute" method.
    _execution_times: int = 10
    # Amount of post to fetch via one "/execute" method execution.
    _posts_per_portion: int = 100

    def _set_total_posts_in_domain(self) -> None:
        """Sets "_total_posts" as amount of posts in the VK domain.
        Not asynchronous as it quickly gets amount of posts to fetch,
        and the amount is used to create asynchronous tasks.
        """
        logger.info(f'Getting total posts in "vk.com/{self.vk_domain}"...')

        params = {
            "v": VKAPI_VERSION,
            "access_token": VKAPI_TOKEN,
            "count": 1,  # Enough just to get total post in domain.
            "domain": self.vk_domain,
        }

        while True:
            response = requests.get(
                self._url_wall_get, params=params, timeout=60
            ).json()

            if "error" in response:
                error = response["error"]

                # If too many requests per second, we'll just wait a bit.
                if error["error_code"] == 6:
                    logger.error(f'{error["error_msg"]}')
                    time.sleep(0.1)
                    continue

                raise _fastapi.HTTPException(status_code=500, detail=error["error_msg"])
            break

        self._total_posts_in_domain = response["response"]["count"]
        logger.info(f"Total posts in VK domain: {self._total_posts_in_domain}")

    async def fetch_posts(self) -> list:
        """
        Fetches posts from VK domain asynchronously.
        :return: a list of posts in the VK domain.
        """

        async def fetch_posts_for_offset(offset) -> list:
            logger.info(
                f'(offset {offset}) Start fetching posts from "vk.com/{self.vk_domain}"...'
            )

            async with ClientSession() as session:
                vks_code = GET_POSTS_TEMPLATE.substitute(
                    {
                        "domain": self.vk_domain,
                        "offset": offset,
                        "posts_per_portion": self._posts_per_portion,
                        "execution_times": self._execution_times,
                    }
                )
                params = {
                    "v": VKAPI_VERSION,
                    "access_token": VKAPI_TOKEN,
                    "code": vks_code,
                }
                url = VKAPI_URL + "execute"

                while True:
                    async with session.get(url=url, params=params) as response:
                        resp_json = await response.json()

                        # If too many requests per second, we'll just wait a bit.
                        if "error" in resp_json:
                            error = resp_json["error"]

                            if error["error_code"] == 6:
                                logger.error(f'{error["error_msg"]}')
                                await asyncio.sleep(delay=0.1)
                                continue

                            raise _fastapi.HTTPException(
                                status_code=500, detail=resp_json["error"]["error_msg"]
                            )

                        logger.info(
                            f'(offset {offset}) End fetching posts from "vk.com/{self.vk_domain}"...'
                        )

                        return resp_json["response"]["items"]

        fetched_posts: list = []
        self._set_total_posts_in_domain()

        if not self._total_posts_in_domain:
            return fetched_posts

        tasks = []
        posts_per_task = self._posts_per_portion * self._execution_times
        offsets = list(range(0, self._total_posts_in_domain, posts_per_task))
        for offset in offsets:
            tasks.append(asyncio.create_task(fetch_posts_for_offset(offset)))

        results = await asyncio.gather(*tasks)

        # Flatting results into one list.
        fetched_posts = [post for result in results for post in result]
        return fetched_posts
