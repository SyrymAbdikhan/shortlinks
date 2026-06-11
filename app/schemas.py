from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel


class LinkCreate(BaseModel):
    url: AnyHttpUrl


class LinkResponse(BaseModel):
    model_config = {"from_attributes": True}

    code: str
    url: str
    created_at: datetime
