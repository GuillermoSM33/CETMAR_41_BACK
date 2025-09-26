from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.dtos.users.get_user_dto import GetUserDTO
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
