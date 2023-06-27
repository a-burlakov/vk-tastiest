from __future__ import print_function

import requests
import sys
import datetime
from datetime import timedelta
from multiprocessing import current_process, cpu_count

from .argparser import parse_args
from .constants import VKAPI_URL, VKAPI_VERSION, APP_ACCESS_KEY
from .utils import get_page_id, VKApiError, pretty_print
from .post import Post


import logging

logging.basicConfig(
    level=logging.INFO,
    format="[\033[92m%(levelname)s %(asctime)s\033[0m]: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
# Removing noisy debug messages from lib request
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logger = logging.getLogger()


class PostDownloader:
    def __init__(self, page_id, from_date=None, to_date=None):
        self.page_id = page_id
        self.api_url = VKAPI_URL + "wall.get"
        self.request_params = {
            "owner_id": self.page_id,
            "v": VKAPI_VERSION,
            "access_token": APP_ACCESS_KEY,
        }
        self.from_date = from_date or datetime.date.min
        self.to_date = to_date or datetime.date.max

    def _number_of_posts(self):
        """Returns total number of post on the page"""

        self.request_params.update({"offset": 0, "count": 1})

        response = requests.get(self.api_url, params=self.request_params).json()

        if "error" in response:
            raise VKApiError(response["error"]["error_msg"])

        total_posts = response["response"]["count"]
        logger.debug("Posts to fetch: {}".format(total_posts))
        return total_posts

    def fetch(self, init_offset=0, num_to_fetch=None):
        """Downloads 'num_to_fetch' posts starting from 'init_offset' position"""
        num_to_fetch = num_to_fetch or self._number_of_posts()

        self.request_params["offset"] = init_offset
        self.request_params["count"] = min(num_to_fetch, 100)

        logger.debug(
            "{} trying to download {} posts".format(
                current_process().name, num_to_fetch
            )
        )

        fetched_posts, fetched_counter = [], 0
        while fetched_counter != num_to_fetch:
            response = requests.get(self.api_url, self.request_params).json()

            if "error" in response:
                raise VKApiError(response["error"]["error_msg"])

            posts = response["response"]["items"]
            fetched_counter += len(posts)

            logger.debug(
                "{} downloaded {}/{} posts".format(
                    current_process().name, fetched_counter, num_to_fetch
                )
            )

            for post in posts:
                post = Post(
                    id=post["id"],
                    text=post["text"],
                    likes=post["likes"]["count"],
                    reposts=post["reposts"]["count"],
                    date=datetime.date.fromtimestamp(post["date"]),
                    url="https://vk.com/wall{}_{}".format(self.page_id, post["id"]),
                )
                if self.from_date <= post.date <= self.to_date:
                    fetched_posts.append(post)

                # Early stopping, all subsequent post should be discarded
                elif post.date < self.from_date:
                    logger.debug(
                        "{} finally returns {} posts".format(
                            current_process().name, len(fetched_posts)
                        )
                    )
                    return fetched_posts

            self.request_params["offset"] += 100
            self.request_params["count"] = min(num_to_fetch - fetched_counter, 100)

        logger.debug(
            "{} returns eventually {} posts".format(
                current_process().name, len(fetched_posts)
            )
        )
        return fetched_posts

    def parallel_fetch(self, max_workers=None):
        """
        Downloads posts in parallel processes.
        Each worker downloads independent segment.
        """

        from concurrent.futures import ProcessPoolExecutor
        from concurrent.futures import as_completed

        # Total number of posts to download
        num_posts = self._number_of_posts()
        num_workers = max_workers or cpu_count()

        fetched_posts = []
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for offset, count in self._distribute_posts(num_posts, num_workers):
                futures.append(executor.submit(self.fetch, offset, count))

            for future in as_completed(futures):
                try:
                    fetched_posts.extend(future.result())
                except Exception as error:
                    logger.error(error)

        return fetched_posts

    def _distribute_posts(self, total_posts, workers):
        """
        Uniformly distributes posts for downloading between workers.
        Returns next start position for downloading and number of posts to fetch.
        """
        per_worker = total_posts // workers + total_posts % workers
        for offset in range(0, total_posts, per_worker):
            if (offset + per_worker) < total_posts:
                yield offset, per_worker
            else:
                yield offset, total_posts - offset


def main():
    args = vars(parse_args())
    if args["verbose"]:
        logger.setLevel(logging.DEBUG)

    if args["days"]:
        if args["from"] or args["to"]:
            logger.error(
                "vktop: error: -d/--days option cannot be used with "
                "-f/--from or -t/--to options"
            )
            sys.exit(1)
        else:
            args["from"] = datetime.date.today() - timedelta(days=args["days"])

    try:
        page_id = get_page_id(args["url"])
    except (RuntimeError, requests.exceptions.ConnectionError) as error:
        logger.error(error)
        sys.exit(1)

    logger.info("Downloading posts. This may take some time, be patient...")

    downloader = PostDownloader(page_id, args["from"], args["to"])

    try:
        if sys.version_info > (3, 0):
            posts = downloader.parallel_fetch(args["workers"])
        else:
            # TODO:
            # Python 2.x does not support concurrent.futures out of the box,
            # therefore in Python 2.x using synchronous downloading
            if args["workers"]:
                logger.warning("Python 2 does not support parallel downloading!")
            posts = downloader.fetch()
    except (KeyboardInterrupt, VKApiError, Exception) as err:
        logger.error(err)
        sys.exit(1)

    logger.debug("Sorting of {} posts".format(len(posts)))

    if args["reposts"]:
        posts = sorted(posts, key=lambda x: (-x.reposts, -x.likes))
    else:
        posts = sorted(posts, key=lambda x: (-x.likes, -x.reposts))

    pretty_print(posts[: args["top"]])


if __name__ == "__main__":
    main()
