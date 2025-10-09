from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import jwt
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.auth_model import AuthModel
from application.services.auth_utils import verify_password, create_access_token
from infrastructure.config.settings import settings
from sqlalchemy import or_
from infrastructure.persistence.models.identity_model import IdentityModel

class AuthService:
    @staticmethod
    def login(identifier: str, password: str, db: Session):
        # Buscar usuario por correo o matrícula
        user = (
            db.query(UserModel)
            .join(IdentityModel, UserModel.FK_Identity_ID == IdentityModel.Id, isouter=True)
            .filter(
                or_(
                    UserModel.User_Email == identifier,
                    IdentityModel.Student_Identity == identifier,
                    IdentityModel.Teacher_Identity == identifier
                )
            )
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado."
            )

        # Buscar hash
        auth = db.query(AuthModel).filter_by(FK_User_ID=user.Id).first()
        if not auth or not verify_password(password, auth.Hashed_Password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas."
            )

        # Generar token JWT
        payload = {
            "sub": str(user.Id),
            "rol": user.role.Role_Name,
            "email": user.User_Email,
            "matricula": user.identity.student_identity or user.identity.teacher_identity
        }

        token = create_access_token(payload)

        return {"access_token": token, "token_type": "bearer"}
