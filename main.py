from pprint import pprint
import requests
import time
import asyncio

from backend.constants import VKAPI_TOKEN, VKAPI_VERSION, VKAPI_URL
from backend.post_fetcher import PostFetcher
from backend.vkscript import GET_POSTS_TEMPLATE


async def fetch_posts():
    post_fetcher = PostFetcher("mudakoff", sort_by_likes=True)

    start = time.perf_counter()
    await post_fetcher.fetch_posts()
    duration = time.perf_counter() - start
    print(duration)

    for post in post_fetcher.posts[:10]:
        print(post.likes, "https://vk.com/" + post.path)


if __name__ == "__main__":
    asyncio.run(fetch_posts())
