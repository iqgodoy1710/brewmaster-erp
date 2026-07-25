from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UnitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    symbol: str = Field(..., min_length=1, max_length=10)


class UnitCreate(UnitBase):
    pass


class UnitResponse(UnitBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)