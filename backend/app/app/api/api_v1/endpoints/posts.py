from fastapi import APIRouter, Query

from services.posts.post_fetcher import PostFetcher
import schemas

router = APIRouter()


@router.get("", status_code=200, response_model=list[schemas.Post])
async def get_posts(
    domain: str = Query(
        title="Адрес человека/сообщества",
        description="Адрес человека/cообщества, в форматах вида "
        '"https://vk.com/a_a_burlakov", "vk.com/a_a_burlakov", "a_a_burlakov"',
    ),
    amount: int = Query(
        title="Количество постов",
        description="Количество постов для загрузки (если 0, будут загружены все)",
        ge=0,
        default=500,
    ),
    sort_by_likes: bool = Query(
        title="Сортировать по лайкам",
        description="Сортировать по лайкам по убыванию "
        "(если False, будет стандартная сортировка по дате)",
        default=True,
    ),
) -> list[schemas.Post]:
    post_fetcher = PostFetcher(domain, amount, sort_by_likes)
    await post_fetcher.fetch_posts()
    return post_fetcher.posts
