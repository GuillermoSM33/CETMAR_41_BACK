from pydantic import BaseModel, Field, constr
from typing import Optional

class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Correo o matrícula")
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AdminResetPasswordDTO(BaseModel):
    new_password: constr(min_length=6) = Field(..., description="Nueva contraseña (mínimo 8 caracteres)")
    force_reset_on_login: Optional[bool] = Field(default=False, description="Forzar cambio en primer login")
