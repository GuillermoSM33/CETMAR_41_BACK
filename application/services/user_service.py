from sqlalchemy.orm import Session
from infrastructure.persistence.models.user_model import UserModel
from application.dtos.users.update_user_dto import UpdateUserDTO
from typing import List

def get_all_users_service(db: Session) -> List[UserModel]:
    return db.query(UserModel).all()

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