from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from application.dtos.students.get_student_dto import GetStudentDetailDTO
from application.dtos.students.update_student_dto import UpdateStudentDTO
from infrastructure.persistence.repositories.db import get_db
from application.services.student_service import import_students_from_csv, get_all_students_service, import_students_from_xls, update_student_service
from typing import List, Any

router = APIRouter()

@router.get("/students", response_model=List[GetStudentDetailDTO])
def get_all_students(db: Session = Depends(get_db)):
    return get_all_students_service(db, "Student")


@router.put("/students/{user_id}", response_model=UpdateStudentDTO)
def update_student(user_id: int, student_data: UpdateStudentDTO, db: Session = Depends(get_db)):
    return update_student_service(db, user_id, student_data)


@router.post("/students/import_xls")
async def import_students_xls(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file.file.seek(0)
        content = file.file.read()
        results = import_students_from_xls(db, content, create_auth=False)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing XLS: {e}")