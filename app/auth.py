from pydantic import BaseModel, EmailStr, Field

class ClinicCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    plan: str = "basic"

class UserCreate(BaseModel):
    clinic_id: int | None = None
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = "staff"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
