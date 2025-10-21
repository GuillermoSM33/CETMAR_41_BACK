from sqlalchemy.orm import Session
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.role_model import RoleModel
from application.dtos.students.update_student_dto import UpdateStudentDTO
from typing import List

def get_all_students_service(db: Session, role_name: str) -> List[UserModel]:
    role = db.query(RoleModel).filter(RoleModel.Role_Name == role_name).first()
    if not role:
        return []
    return db.query(UserModel).filter(UserModel.FK_Rol_ID == role.Id).all()

def update_student_service(db: Session, user_id: int, student_data: UpdateStudentDTO) -> UserModel:
    student = db.query(UserModel).filter(UserModel.Id == user_id).first()
    if not student:
        raise Exception("Usuario no encontrado")

    student.User_Name = student_data.User_Name
    student.User_Email = student_data.User_Email
    student.FK_Rol_ID = student_data.FK_Rol_ID
    student.Telephone = int(student_data.Telephone)
    student.FK_Identity_ID = student_data.FK_Identity_ID

    db.commit()
    db.refresh(student)
    return student