from pprint import pprint
import requests

from backend.constants import VKAPI_TOKEN, VKAPI_VERSION, VKAPI_URL
from backend.post_fetcher import PostFetcher
from backend.vkscript import GET_2500_POSTS_TEMPLATE


if __name__ == "__main__":
    domain = "repouiii"
    post_fetcher = PostFetcher(domain)
    posts = post_fetcher.fetch_posts_synchronously()
    pprint(posts)
