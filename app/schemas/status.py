from pydantic import BaseModel


class StatusCreateIn(BaseModel):
    name: str
    description: str | None = None


class StatusCreateOut(StatusCreateIn):
    id: int


class StatusListOut(StatusCreateOut):
    ...


class StatusUpdateIn(BaseModel):
    name: str | None = None
    description: str | None = None


class StatusUpdateOut(StatusCreateOut):
    ...