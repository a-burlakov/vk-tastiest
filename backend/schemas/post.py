import datetime
import pydantic as pydantic
from pydantic import Field


class PostPhoto(pydantic.BaseModel):
    """VK post photos data."""

    url: str = Field(description="Путь URL к фотографии")


class PostVideo(pydantic.BaseModel):
    """VK post videos data."""

    first_frame_url: str = Field(description="Путь URL к первому кадру видео")


class Post(pydantic.BaseModel):
    """VK post data."""

    date: datetime.datetime = Field(description="Дата поста")
    likes: int = Field(description="Количество лайков")
    text: str = Field(description="Текст поста")
    path: str = Field(description="Путь URL к посту")
    photos: list[PostPhoto] = Field(description="Фотографии в посте")
    videos: list[PostVideo] = Field(description="Видео в посте")
