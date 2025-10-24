from fastapi import APIRouter, Depends, Body, status
from sqlalchemy.orm import Session
from application.dtos.auth.auth_dto import LoginRequest, LoginResponse, AdminResetPasswordDTO
from application.services.auth_service import AuthService
from presentation.api.v1.dependencies.auth_dependencies import admin_required
from application.services.auth_service import AuthService
from infrastructure.persistence.repositories.db import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(request.identifier, request.password, db)


@router.post("/admin/reset-password/{user_id}", status_code=status.HTTP_200_OK)
def admin_reset_password(
    user_id: int,
    payload: AdminResetPasswordDTO,
    db: Session = Depends(get_db),
    admin_user: dict = Depends(admin_required),
):
    # payload es un Pydantic model; acceder con atributos
    new_password = payload.new_password
    return AuthService.admin_reset_password(admin_user, user_id, new_password, db)

