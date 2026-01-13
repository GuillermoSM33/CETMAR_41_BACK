from datetime import date
import sys, os
# Asegura que las rutas de importación funcionen si el script se ejecuta de forma independiente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))) 

import bcrypt

from infrastructure.persistence.repositories.db import SessionLocal
from infrastructure.persistence.models.role_model import RoleModel
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.token_model import TokenModel
from infrastructure.persistence.models.identity_model import IdentityModel
from infrastructure.persistence.models.auth_model import AuthModel 


def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def seed_data():
    session = SessionLocal()

    try:
        # 1. --- Roles ---
        admin_role = RoleModel(Role_Name="Admin")
        teacher_role = RoleModel(Role_Name="Control School")
        director_role = RoleModel(Role_Name="Director")
        vinculation_role = RoleModel(Role_Name="Vinculation")
        student_role = RoleModel(Role_Name="Student")
        management_admin_role = RoleModel(Role_Name="Management Admin")
        session.add_all([admin_role, teacher_role, director_role, vinculation_role, student_role, management_admin_role])
        session.commit()

        # 2. --- Identidades ---
        identity1 = IdentityModel(
             Student_Control_Number="SCN-0001", Full_Name="Guillermo Garcia Canul", Teacher_Identity=0, Management_Admin_Identity=1, Schedule="morning"
        )
        identity2 = IdentityModel(
             Student_Control_Number="SCN-0002", Full_Name="Alisson", Teacher_Identity=2001, Management_Admin_Identity=0, Schedule="evening"
        )
        identity3 = IdentityModel(
             Student_Control_Number="SCN-0003", Full_Name="Aysha Medina Garcia", Student_Identity=22393204, Teacher_Identity=None, Management_Admin_Identity=0, Schedule="evening", Major="Ingeniería en desarrollo biomédico"
        )
        session.add_all([identity1, identity2, identity3])
        session.commit()

        # 3. --- Usuarios ---
        user1 = UserModel(
             User_Name="Guillermo Garcia Canul", User_Email="guillermo.jesus.garcia.canul@gmail.com", FK_Rol_ID=admin_role.Id, Telephone=9983187269, FK_Identity_ID=identity1.Id
        )
        user2 = UserModel(
             User_Name="Alisson", User_Email="alisson@gmail.com", FK_Rol_ID=teacher_role.Id, Telephone=9983187269, FK_Identity_ID=identity2.Id
        )
        user3 = UserModel(
             User_Name="Aysha Medina Garcia", User_Email="aysha_medina_garcia@gmail.com", FK_Rol_ID=student_role.Id, Telephone=9983187269, FK_Identity_ID=identity3.Id
        )
        session.add_all([user1, user2, user3])
        session.commit()  # Commit para que userX.Id esté disponible.

        # 4. --- Contraseñas (AuthModel) ---
        password_admin_teacher = "123456"
        password_aysha = "54321"

        hash1 = get_hashed_password(password_admin_teacher)
        hash2 = get_hashed_password(password_admin_teacher)
        hash3 = get_hashed_password(password_aysha)

        auth1 = AuthModel(FK_User_ID=user1.Id, Hashed_Password=hash1)
        auth2 = AuthModel(FK_User_ID=user2.Id, Hashed_Password=hash2)
        auth3 = AuthModel(FK_User_ID=user3.Id, Hashed_Password=hash3)

        session.add_all([auth1, auth2, auth3])
        session.commit()

        # 5. --- Tokens ---
        token1 = TokenModel(Token="abc123", InBlackList=False, Date_Expiration_Time=date(2025, 12, 31), FK_User_ID=user1.Id)
        token2 = TokenModel(Token="def456", InBlackList=True, Date_Expiration_Time=date(2025, 11, 15), FK_User_ID=user2.Id)
        session.add_all([token1, token2])
        session.commit()

        print("Datos dummy insertados correctamente (incluyendo contraseñas hasheadas en AuthModel)")

    except Exception as e:
        print(f"Error durante el seed: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()
