from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.dtos.users.get_user_dto import GetUserDTO
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.repositories.db import get_db  
from typing import List

router = APIRouter()

@router.get("/users", response_model=List[GetUserDTO])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()

@router.update("/edit/user/{$}", response_model=List[UpdateUserDTO])
def update_user(db: Session = Depends(get_db)):
    return db.query(UserModel)
