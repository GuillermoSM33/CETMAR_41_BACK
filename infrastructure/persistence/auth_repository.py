from sqlalchemy.orm import Session
from infrastructure.persistence.models.auth_model import AuthModel
from sqlalchemy import select

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_identifier(self, identifier: str):
        """
        Busca la contraseña del usuario usando correo o matrícula.
        Devuelve el AuthModel con la relación user cargada.
        """
        stmt = select(AuthModel).join(AuthModel.user).where(
            (AuthModel.user.User_Email == identifier) | (AuthModel.user.User_Name == identifier)
        )
        return self.db.execute(stmt).scalar_one_or_none()
