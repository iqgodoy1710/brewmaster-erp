from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BottlePasteurizationRunCreate(BaseModel):
    beer_presentation_id: int = Field(..., gt=0)
    processed_quantity: int = Field(..., gt=0)
    approved_quantity: int = Field(..., ge=0)
    notes: str | None = None
    occurred_at: datetime | None = None

    model_config = ConfigDict(extra="forbid")


class BottlePasteurizationRunResponse(BaseModel):
    id: int
    code: str
    beer_presentation_id: int
    processed_quantity: int
    approved_quantity: int
    waste_quantity: int
    performed_by_user_id: int | None
    occurred_at: datetime
    notes: str | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)