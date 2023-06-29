import datetime
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.core.config import settings

FAKE_GOOD_POSTS_CASES = [
    [
        {
            "date": datetime.datetime.utcnow(),
            "likes": 123,
            "text": "text",
            "path": "path",
            "photos": [
                {"url": "url-1"},
                {"url": "url-2"},
            ],
            "videos": [
                {"first_frame_url": "url-1"},
                {"first_frame_url": "url-2"},
            ],
        },
        {
            "date": datetime.datetime.utcnow(),
            "likes": 444,
            "text": "text2",
            "path": "path3",
            "photos": [],
            "videos": [],
        },
    ],
]

FAKE_BAD_POSTS_CASES = [
    [
        {
            "date": datetime.datetime.utcnow(),
        },
    ],
    [
        {
            "date": datetime.datetime.utcnow(),
            "liked": 123,
            "text": "text",
            "path": "path",
            "photos": [
                {"url": "url-1"},
                {"url": "url-2"},
            ],
            "videos": [
                {"first_frame_url": "url-1"},
                {"first_frame_url": "url-2"},
            ],
        },
    ],
    [
        {
            "date": datetime.datetime.utcnow(),
            "likes": 123,
            "text": "text",
            "path": "path",
            "photos": [
                {"first_frame_url": "url-1"},
                {"first_frame_url": "url-2"},
            ],
            "videos": [
                {"url": "url-1"},
                {"url": "url-2"},
            ],
        },
    ],
]


@pytest.fixture(autouse=True)
def patch_post_fetcher(mocker):
    mocker.patch(
        "backend.services.posts.post_fetcher.PostFetcher.fetch_posts",
        side_effect=None,
    )


def test_get_posts_no_parameters(client: TestClient) -> None:
    """Calling endpoint with no parameters."""
    resp = client.get(f"{settings.API_V1_STR}/posts")
    assert resp.status_code == 422


@pytest.mark.parametrize("fake_good_posts", FAKE_GOOD_POSTS_CASES)
def test_get_posts_good_posts(client: TestClient, mocker, fake_good_posts) -> None:
    """Returning valid data from endpoint."""
    mocker.patch(
        "backend.services.posts.post_fetcher.PostFetcher.posts",
        new_callable=mocker.PropertyMock,
        return_value=fake_good_posts,
    )
    client.get(f"{settings.API_V1_STR}/posts?domain=vk.com/a_a_burlakov")
    assert True


@pytest.mark.parametrize("fake_bad_posts", FAKE_BAD_POSTS_CASES)
def test_get_posts_bad_posts(client: TestClient, mocker, fake_bad_posts) -> None:
    """Returning non-valid data from endpoint."""
    # mocker.patch(
    #     "backend.services.posts.post_fetcher.PostFetcher.fetch_posts",
    #     side_effect=None,
    # )
    mocker.patch(
        "backend.services.posts.post_fetcher.PostFetcher.posts",
        new_callable=mocker.PropertyMock,
        return_value=fake_bad_posts,
    )

    try:
        client.get(f"{settings.API_V1_STR}/posts?domain=a_a_burlakov")
    except ValidationError:
        assert True
    except Exception:
        assert False
    else:
        assert False
