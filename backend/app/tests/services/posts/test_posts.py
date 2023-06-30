import datetime

import pytest
from fastapi import HTTPException

from schemas import Post, PostPhoto, PostVideo
from services.posts.post_fetcher import PostFetcher


def test_set_total_posts_in_domain(requests_mock):
    post_fetcher = PostFetcher("a_a_burlakov")
    fake_total_posts_in_domain = 333
    fake_response = {"response": {"count": fake_total_posts_in_domain}}

    requests_mock.get(post_fetcher._url_wall_get, json=fake_response)

    post_fetcher._set_total_posts_in_domain()

    assert post_fetcher._total_posts_in_domain == fake_total_posts_in_domain


def test_set_total_posts_in_domain_bad_response(requests_mock):
    post_fetcher = PostFetcher("a_a_burlakov")
    fake_response = {
        "error": {
            "error_code": 42,
            "error_msg": "how could you",
        },
    }
    requests_mock.get(post_fetcher._url_wall_get, json=fake_response)

    try:
        post_fetcher._set_total_posts_in_domain()
    except HTTPException:
        assert True
    else:
        assert False


class MockAsyncResponse:
    def __init__(self, _json, status):
        self._json = _json
        self.status = status

    async def json(self):
        return self._json

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@pytest.mark.asyncio
async def test_fetch_posts(mocker, requests_mock):
    # Fake responses.
    fake_total_posts_in_domain = 42
    fake_response_count = {"response": {"count": fake_total_posts_in_domain}}

    fake_response_posts = {
        "response": {
            "items": [
                {
                    "id": "55123",
                    "owner_id": "44412",
                    "date": datetime.datetime(2023, 6, 29, 0, 1, 2),
                    "likes": {"count": 42},
                    "text": "text",
                    "path": "path",
                    "attachments": [
                        {
                            "type": "photo",
                            "photo": {
                                "sizes": [
                                    {"url": "photo-url"},
                                ]
                            },
                        }
                    ],
                },
                {
                    "id": "1233",
                    "owner_id": "44412",
                    "date": datetime.datetime(2023, 6, 29, 0, 1, 2),
                    "likes": {"count": 444},
                    "text": "text",
                    "path": "path",
                    "attachments": [
                        {
                            "type": "video",
                            "video": {
                                "first_frame": [
                                    {"url": "video-url-1"},
                                ]
                            },
                        },
                        {
                            "type": "video",
                            "video": {
                                "image": [
                                    {"url": "video-url-2"},
                                ]
                            },
                        },
                    ],
                },
            ]
        }
    }

    # Expected result.
    expected_posts = [
        Post(
            date=datetime.datetime(2023, 6, 29, 0, 1, 2),
            likes=42,
            text="text",
            path="wall44412_55123",
            photos=[
                PostPhoto(url="photo-url"),
            ],
            videos=[],
        ),
        Post(
            date=datetime.datetime(2023, 6, 29, 0, 1, 2),
            likes=444,
            text="text",
            path="wall44412_1233",
            photos=[],
            videos=[
                PostVideo(first_frame_url="video-url-1"),
                PostVideo(first_frame_url="video-url-2"),
            ],
        ),
    ]

    amount_to_fetch = 50
    post_fetcher = PostFetcher("vk_com/a_a_burlakov", amount_to_fetch)

    # Mocked synchronous call.
    requests_mock.get(post_fetcher._url_wall_get, json=fake_response_count)

    # Mocked asynchronous call.
    resp = MockAsyncResponse(fake_response_posts, status=200)
    mocker.patch("aiohttp.ClientSession.get", return_value=resp)

    # Starting fetching.
    await post_fetcher.fetch_posts()

    # Asserting.
    assert post_fetcher.vk_domain == "a_a_burlakov"
    assert post_fetcher.amount_to_fetch == amount_to_fetch
    assert post_fetcher._total_posts_in_domain == fake_total_posts_in_domain
    assert post_fetcher.posts == expected_posts
    assert post_fetcher.posts == post_fetcher._posts
