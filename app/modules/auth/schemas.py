from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nombre: str = Field(min_length=1, max_length=100)
    zona: str | None = None

class UsuarioOut(BaseModel):
    id: int
    email: EmailStr
    nombre: str
    zona: str | None
    foto_url: str | None
    rol: str
    created_at: datetime

    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"