from fastapi import APIRouter

from backend import schemas
from backend.services.posts.post_fetcher import PostFetcher

router = APIRouter()


@router.get("/most_popular/", status_code=200, response_model=list[schemas.Post])
async def most_popular(domain: str, sort_by_likes: bool = True) -> list[schemas.Post]:
    post_fetcher = PostFetcher(domain, sort_by_likes=sort_by_likes)
    await post_fetcher.fetch_posts()
    return post_fetcher.posts[:10]
