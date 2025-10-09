from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy import or_
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.auth_model import AuthModel
from infrastructure.persistence.models.identity_model import IdentityModel
from application.services.auth_utils import verify_password, create_access_token


class AuthService:
    @staticmethod
    def login(identifier: str, password: str, db: Session):
        # Detectar tipo de identifier, para que sea int (matricula) o str (email)
        identifier_email = None
        identifier_student = None
        identifier_teacher = None

        if "@" in identifier:
            identifier_email = identifier
        else:
            try:
                identifier_int = int(identifier)
                identifier_student = identifier_int
                identifier_teacher = identifier_int
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Identificador inválido. Debe ser correo o matrícula numérica."
                )

        # Construir filtros solo con los valores válidos, verificando que exista alguno
        filters = []
        if identifier_email:
            filters.append(UserModel.User_Email == identifier_email)
        if identifier_student:
            filters.append(IdentityModel.Student_Identity == identifier_student)
        if identifier_teacher:
            filters.append(IdentityModel.Teacher_Identity == identifier_teacher)

        user = (
            db.query(UserModel)
            .join(IdentityModel, UserModel.FK_Identity_ID == IdentityModel.Id, isouter=True)
            .filter(or_(*filters))
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado."
            )

        
        auth = db.query(AuthModel).filter_by(FK_User_ID=user.Id).first()
        if not auth or not verify_password(password, auth.Hashed_Password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas."
            )

        # Obtener rol del usuario
        role_name = user.role.Role_Name if user.role else None

        # Obtener identifier (de alumno o docente)
        matricula = None
        if user.identity:
            matricula = user.identity.Student_Identity or user.identity.Teacher_Identity

        payload = {
            "sub": str(user.Id),
            "rol": role_name,
            "email": user.User_Email,
            "matricula": matricula
        }

        token = create_access_token(payload)

        return {"access_token": token, "token_type": "bearer"}
