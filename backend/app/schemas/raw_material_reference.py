from pydantic import BaseModel, ConfigDict


class RawMaterialReferenceResponse(BaseModel):
    id: int
    code: str
    name: str
    category_id: int
    unit_symbol: str

    model_config = ConfigDict(from_attributes=True)