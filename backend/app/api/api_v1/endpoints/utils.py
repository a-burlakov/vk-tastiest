from typing import Any
from fastapi import APIRouter

from backend import schemas

router = APIRouter()


@router.get("/health/{message}", response_model=schemas.Msg)
def health_check(message: str) -> Any:
    return {"msg": f"Success! Got message - {message}."}
