from pprint import pprint
import requests
import time

from backend.constants import VKAPI_TOKEN, VKAPI_VERSION, VKAPI_URL
from backend.post_fetcher import PostFetcher
from backend.vkscript import GET_2500_POSTS_TEMPLATE


if __name__ == "__main__":
    domain = "repouiii"

    start = time.perf_counter()
    post_fetcher = PostFetcher(domain)

    # posts = post_fetcher.fetch_posts_synchronously()
    # duration = time.perf_counter() - start
    # print(duration)
    # # pprint(posts)
