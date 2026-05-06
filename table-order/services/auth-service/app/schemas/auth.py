from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    store_code: str = Field(..., max_length=50)
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=128)


class TableLoginRequest(BaseModel):
    store_code: str = Field(..., max_length=50)
    table_number: int = Field(..., gt=0)
    password: str = Field(..., max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: str


class TableTokenResponse(TokenResponse):
    table_id: int
    table_number: int
    store_id: int


class UserInfo(BaseModel):
    user_id: int
    store_id: int
    user_type: str
    table_number: int | None = None
