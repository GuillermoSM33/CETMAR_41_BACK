from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from application.dtos.students.get_student_dto import GetStudentDTO
from application.dtos.students.update_student_dto import UpdateStudentDTO
from infrastructure.persistence.repositories.db import get_db  
from application.services.student_service import *
from typing import List

router = APIRouter()

@router.get("/students", response_model=List[GetStudentDTO])
def get_all_students(db: Session = Depends(get_db)):
    return get_all_students_service(db, "student")

@router.put("/students/{user_id}", response_model=UpdateStudentDTO)
def update_student(user_id: int, student_data: UpdateStudentDTO, db: Session = Depends(get_db)):
    return update_student_service(db, user_id, student_data)