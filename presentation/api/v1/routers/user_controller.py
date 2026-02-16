from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from application.dtos.users.get_user_dto import GetUserDTO
from application.dtos.users.create_user_dto import CreateUserDTO
from application.dtos.users.update_user_dto import UpdateUserDTO
from infrastructure.persistence.repositories.db import get_db  
from application.services.user_service import *
from typing import List

router = APIRouter()

@router.get("/users", response_model=List[GetUserDTO])
def get_all_users(db: Session = Depends(get_db)):
    return get_all_users_service(db)

@router.put("/users/{user_id}", response_model=UpdateUserDTO)
def update_user(user_id: int, user_data: UpdateUserDTO, db: Session = Depends(get_db)):
    return update_user_service(db, user_id, user_data)

@router.get("/users/count")
def get_user_count(db: Session = Depends(get_db)):
    return {"total_usuarios": count_users_service(db)}

@router.patch("/users/create", response_model=GetUserDTO)
def create_users(user_data: CreateUserDTO, db: Session = Depends(get_db)):
    try:
        return create_user_service(db, user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="Conflicto de integridad al crear usuario") from e
