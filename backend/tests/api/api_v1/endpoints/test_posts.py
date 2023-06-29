from fastapi.testclient import TestClient
from unittest.mock import patch, PropertyMock

from backend.core.config import settings
from backend.services.posts.post_fetcher import PostFetcher


# тут просто, мокаем postfetcher, он там у себя какие-то делает посты
# два теста: с плохими постами и хорошими, чтобы схемы проверить
def test_get_posts_no_parameters(client: TestClient) -> None:
    resp = client.get(f"{settings.API_V1_STR}/posts")
    assert resp.status_code == 422


def test_get_posts_good_posts(client: TestClient, mocker) -> None:
    fake_response = {"name": "FAKE_NAME", "age": "FAKE_AGE", "address": "FAKE_ADDRESS"}
    mocker.patch(
        "backend.services.posts.post_fetcher.PostFetcher.fetch_posts",
        side_effect=None,
    )
    mocker.patch(
        "backend.services.posts.post_fetcher.PostFetcher.posts",
        new_callable=mocker.PropertyMock,
        return_value=fake_response,
    )

    resp = client.get(f"{settings.API_V1_STR}/posts?domain=a_a_burlakov")
    resp_json = resp.json()
    a = 1
