from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BeerBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    style: str | None = Field(default=None, max_length=50)
    description: str | None = None


class BeerCreate(BeerBase):
    model_config = ConfigDict(extra="forbid")


class BeerResponse(BeerBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)