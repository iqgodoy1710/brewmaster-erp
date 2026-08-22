from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9._-]+$",
    )
    password: str = Field(..., min_length=1, max_length=128)

    model_config = ConfigDict(extra="forbid")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
