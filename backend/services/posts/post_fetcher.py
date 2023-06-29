"""
Services for post fetching from VK domains.
"""
import logging
import asyncio
from dataclasses import dataclass, field

from backend.schemas.post import Post, PostPhoto, PostVideo
from backend.services.vkontakte.vk_api import (
    vk_synchronous_request,
    vk_asynchronous_request,
)
from backend.services.vkontakte.vk_script import get_wall_post_template
from backend.core.config import settings

logging.basicConfig(**settings.LOGGING_STANDARD_PARAMS)
logger = logging.getLogger(__name__)


@dataclass
class PostFetcher:
    """
    Fetches posts from VK group or person.
    """

    vk_domain: str  # Group or person address in VK, e.g. "a_a_burlakov".
    amount_to_fetch: int = 0  # If 0, will gather all posts.
    sort_by_likes: bool = False

    _url_wall_get = settings.VKAPI_URL + "wall.get"
    _url_execute = settings.VKAPI_URL + "execute"

    _total_posts_in_domain: int = 0
    _posts: list[Post] = field(default_factory=list)

    # Number of times to execute query via "/execute" method.
    _execution_times: int = 5
    # Amount of post to fetch via one "/execute" method execution.
    _posts_per_portion: int = 100

    def __post_init__(self):
        # Compressing domain.
        if "/" in self.vk_domain:
            self.vk_domain = self.vk_domain.split("/")[-1]

    @property
    def posts(self) -> list[Post]:
        return self._posts

    def _set_total_posts_in_domain(self) -> None:
        """Sets "_total_posts" as amount of posts in the VK domain.
        Not asynchronous as it quickly gets amount of posts to fetch,
        and the amount is used to create asynchronous tasks.
        """
        logger.info('Getting total posts in "vk.com/%s"...', self.vk_domain)

        params = {
            "v": settings.VKAPI_VERSION,
            "access_token": settings.VKAPI_TOKEN,
            "count": 1,  # Enough just to get total post in domain.
            "domain": self.vk_domain,
        }

        # Data fetching.
        response = vk_synchronous_request(
            self._url_wall_get,
            params,
            domain=self.vk_domain,
        )

        self._total_posts_in_domain = response["response"]["count"]
        logger.info("Total posts in VK domain: %s", self._total_posts_in_domain)

    async def fetch_posts(self) -> None:
        """
        Fetches posts from VK domain asynchronously and
        put it into "posts" attribute.
        """

        async def fetch_posts_for_offset(offset) -> list:
            logger.info(
                "(offset %i) Start fetching posts from vk.com/%s...",
                offset,
                self.vk_domain,
            )

            # VK Script code for /execute method.
            vks_code = get_wall_post_template.substitute(
                {
                    "domain": self.vk_domain,
                    "offset": offset,
                    "posts_per_portion": self._posts_per_portion,
                    "execution_times": self._execution_times,
                }
            )
            params = {
                "v": settings.VKAPI_VERSION,
                "access_token": settings.VKAPI_TOKEN,
                "code": vks_code,
            }
            url = self._url_execute

            # Posts fetching.
            resp_json = await vk_asynchronous_request(
                url,
                params,
                domain=self.vk_domain,
                offset=offset,
            )

            logger.info(
                "(offset %i) End fetching posts from vk.com/%s...",
                offset,
                self.vk_domain,
            )

            # Gathered posts handling.
            posts_from_vk = resp_json["response"]["items"]
            posts = posts_as_schemas(posts_from_vk)
            del posts_from_vk
            return posts

        # Checks and preparations.
        self._set_total_posts_in_domain()
        if not self._total_posts_in_domain:
            return

        # amount_to_fetch = self._total_posts_in_domain
        # if self.amount_to_fetch:
        #     amount_to_fetch = self.amount_to_fetch

        # Creating tasks for fetching.
        tasks = []
        posts_per_task = self._posts_per_portion * self._execution_times
        offsets = list(range(0, self._total_posts_in_domain, posts_per_task))
        for offset in offsets:
            tasks.append(asyncio.create_task(fetch_posts_for_offset(offset)))

        # Running tasks.
        logger.info("Start fetching posts from vk.com/%s...", self.vk_domain)
        results = await asyncio.gather(*tasks)
        logger.info("End fetching posts from vk.com/%s...", self.vk_domain)

        # Flatting results from many tasks into one list.
        self._posts = [post for result in results for post in result]

        # Final actions.
        if self.sort_by_likes:
            self._posts = list(sorted(self.posts, key=lambda p: p.likes, reverse=True))
        if self.amount_to_fetch:
            self._posts = self._posts[: self.amount_to_fetch]


def posts_as_schemas(posts_from_vk: list[dict]) -> list[Post]:
    """
    Creates posts as Pydantic schemas based on posts data given
    from VK API.
    :param posts_from_vk: list of posts as dicts from VK API
    :return: list of posts as Pydantic objects
    """
    posts = []

    for post_from_vk in posts_from_vk:
        try:
            post = Post(
                date=post_from_vk["date"],
                likes=post_from_vk["likes"]["count"],
                text=post_from_vk["text"],
                path=f"wall{post_from_vk['owner_id']}_" f"{post_from_vk['id']}",
                photos=[],
                videos=[],
            )
        except KeyError as exc:
            logger.error("No key %s for post: %s", exc, post_from_vk)
            continue

        # Collect attachments (photos, videos etc.).
        if "attachments" in post_from_vk:
            attachments = post_from_vk["attachments"]
            for attachment in attachments:
                if attachment["type"] == "photo":
                    try:
                        photo = PostPhoto(url="")
                        photo.url = attachment["photo"]["sizes"][-1]["url"]
                        post.photos.append(photo)
                    except KeyError as exc:
                        logger.error("No key %s for photo: %s", exc, post_from_vk)

                elif attachment["type"] == "video":
                    video = PostVideo(first_frame_url="")
                    video_from_vk = attachment["video"]
                    if "first_frame" in video_from_vk:
                        video.first_frame_url = video_from_vk["first_frame"][-1]["url"]
                    elif "image" in video_from_vk:
                        video.first_frame_url = video_from_vk["image"][-1]["url"]
                    else:
                        logger.error("No video image found: %s", post)
                        continue
                    post.videos.append(video)

        posts.append(post)

    return posts
