from pprint import pprint
import requests
import time
import asyncio

from backend.constants import VKAPI_TOKEN, VKAPI_VERSION, VKAPI_URL
from backend.post_fetcher import PostFetcher
from backend.vkscript import GET_POSTS_TEMPLATE


async def fetch_posts():
    domain = "te_ekb"
    # domain = "repouiii"
    post_fetcher = PostFetcher(domain)

    start = time.perf_counter()
    posts = await post_fetcher.fetch_posts_asynchronously()
    duration = time.perf_counter() - start
    print(duration)

    start = time.perf_counter()
    posts = post_fetcher.fetch_posts_synchronously()
    duration = time.perf_counter() - start
    print(duration)

    # pprint(len(posts))


if __name__ == "__main__":
    asyncio.run(fetch_posts())
