from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.dtos.auth_dto import LoginRequest, LoginResponse
from application.services.auth_service import AuthService
from infrastructure.persistence.repositories.db import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login(request.identifier, request.password, db)
