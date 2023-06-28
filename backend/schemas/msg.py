from pydantic import BaseModel


class Msg(BaseModel):
    """Plainest message."""

    msg: str
