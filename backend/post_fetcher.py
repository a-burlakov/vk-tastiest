from dataclasses import dataclass
import requests
import fastapi as _fastapi

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
