import secrets
import logging

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, validator

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = ["http://localhost:3000"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "VK Tastiest"

    VKAPI_URL = "https://api.vk.com/method/"
    VKAPI_VERSION = "5.131"
    VKAPI_TOKEN: str

    LOGGING_STANDARD_PARAMS = {
        "level": logging.INFO,
        "format": "[\033[92m%(levelname)s %(asctime)s\033[0m]: %(message)s",
        "datefmt": "%m/%d/%Y %I:%M:%S %p",
    }

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
