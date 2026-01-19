from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy import or_
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.auth_model import AuthModel
from infrastructure.persistence.models.identity_model import IdentityModel
from application.utils.auth_utils import verify_password, create_access_token
import bcrypt


class AuthService:
    @staticmethod
    def login(identifier: str, password: str, db: Session):
        # Detectar tipo de identifier: email, número de control (string) o identidad numérica (docente)
        identifier_email = None
        identifier_teacher = None
        identifier_control_number = None

        if "@" in identifier:
            identifier_email = identifier
        else:
            identifier_str = identifier.strip()
            if not identifier_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Identificador inválido. Debe ser correo, número de control o identidad numérica."
                )

            # Student_Control_Number is stored as string (may be numeric)
            identifier_control_number = identifier_str

            # Teacher_Identity is integer
            if identifier_str.isdigit():
                try:
                    identifier_teacher = int(identifier_str)
                except ValueError:
                    identifier_teacher = None

        # Construir filtros solo con los valores válidos, verificando que exista alguno
        filters = []
        if identifier_email:
            filters.append(UserModel.User_Email == identifier_email)
        if identifier_control_number:
            filters.append(IdentityModel.Student_Control_Number == identifier_control_number)
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
        control_number = None
        teacher_identity = None
        if user.identity:
            control_number = user.identity.Student_Control_Number
            teacher_identity = user.identity.Teacher_Identity

        payload = {
            "sub": str(user.Id),
            "rol": role_name,
            "email": user.User_Email,
            # Backwards-compatible field name used by some clients
            "matricula": control_number or teacher_identity,
            "control_number": control_number,
            "teacher_identity": teacher_identity,
        }

        token = create_access_token(payload)

        return {"access_token": token, "token_type": "bearer"}

    @staticmethod
    def admin_reset_password(admin_user: dict, target_user_id: int, new_password: str, db: Session, force_reset: bool = False):
        """
        Resetea la contraseña de un usuario (endpoint administrativo).
        - admin_user: dict con la información del usuario que solicita (ej. payload del JWT).
        - target_user_id: id del usuario objetivo.
        - new_password: nueva contraseña en texto plano.
        - db: Session de SQLAlchemy.
        """
        role = (admin_user.get("rol") or admin_user.get("role_name") or "").lower()
        if role not in ("admin", "director", "management_admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado para cambiar contraseñas.")

        user = db.query(UserModel).filter(UserModel.Id == target_user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")

        if len(new_password.strip()) < 6 or " " in new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña inválida. Debe tener al menos 6 caracteres y no contener espacios.")

        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        auth = db.query(AuthModel).filter(AuthModel.FK_User_ID == user.Id).first()
        if auth:
            auth.Hashed_Password = hashed_pw
        else:
            auth = AuthModel(FK_User_ID=user.Id, Hashed_Password=hashed_pw)
            db.add(auth)

        db.commit()
        return {"detail": f"Contraseña del usuario {user.User_Name} actualizada correctamente."}
