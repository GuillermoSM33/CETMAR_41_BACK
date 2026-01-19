from sqlalchemy.orm import Session
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.identity_model import IdentityModel
from infrastructure.persistence.models.role_model import RoleModel
from application.dtos.users.update_user_dto import UpdateUserDTO
from application.dtos.users.create_user_dto import CreateUserDTO
from infrastructure.persistence.repositories.user_repository import get_user_count
from typing import List

def get_all_users_service(db: Session) -> List[UserModel]:
    return db.query(UserModel).all()

def create_user_service(db: Session, user_data: CreateUserDTO) -> UserModel:
    try:
        role = db.query(RoleModel).filter(RoleModel.Id == user_data.FK_Rol_ID).first()
        if not role:
            raise ValueError(f"Rol no encontrado: FK_Rol_ID={user_data.FK_Rol_ID}")

        new_identity = IdentityModel(
            Student_Control_Number=user_data.Student_Control_Number,
            CURP=user_data.CURP,
            Full_Name=user_data.Full_Name,
            Teacher_Identity=user_data.Teacher_Identity,
            Schoolar_Control_Identity=user_data.Schoolar_Control_Identity,
            Director_Identity=user_data.Director_Identity,
            Management_Admin_Identity=user_data.Management_Admin_Identity,
            Grupo=user_data.Grupo,
            Schedule=user_data.Schedule,
            Major=user_data.Major,
        )
        db.add(new_identity)
        db.flush() 

        new_user = UserModel(
            User_Name=user_data.User_Name,
            User_Email=user_data.User_Email,
            Telephone=int(user_data.Telephone),
            FK_Rol_ID=user_data.FK_Rol_ID,
            FK_Identity_ID=new_identity.Id,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception:
        db.rollback()
        raise

def update_user_service(db: Session, user_id: int, user_data: UpdateUserDTO) -> UserModel:
    user = db.query(UserModel).filter(UserModel.Id == user_id).first()
    if not user:
        raise Exception("Usuario no encontrado")

    user.User_Name = user_data.User_Name
    user.User_Email = user_data.User_Email
    user.FK_Rol_ID = user_data.FK_Rol_ID
    user.Telephone = int(user_data.Telephone)
    user.FK_Identity_ID = user_data.FK_Identity_ID

    db.commit()
    db.refresh(user)
    return user


def count_users_service(db):
    """Lógica de negocio para contar usuarios"""
    return get_user_count(db)
