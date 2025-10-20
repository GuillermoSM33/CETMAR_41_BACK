from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Correo o matrícula")
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
