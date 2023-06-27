import datetime
import pydantic as pydantic


class PostPhotos(pydantic.BaseModel):
    url: str


class PostVideos(pydantic.BaseModel):
    first_frame_url: str


class Post(pydantic.BaseModel):
    date: datetime.datetime
    likes: int
    path: str
    photos: list[PostPhotos]
    videos: list[PostVideos]
