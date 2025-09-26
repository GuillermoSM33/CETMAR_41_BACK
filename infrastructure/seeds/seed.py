from datetime import date
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from infrastructure.persistence.repositories.db import SessionLocal
from infrastructure.persistence.models.role_model import RoleModel
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.token_model import TokenModel
from infrastructure.persistence.models.identity_model import IdentityModel


def seed_data():
    session = SessionLocal()

    try:
        # --- Roles ---
        admin_role = RoleModel(Role_Name="Admin")
        teacher_role = RoleModel(Role_Name="Teacher")
        student_role = RoleModel(Role_Name="Student")
        session.add_all([admin_role, teacher_role, student_role])
        session.commit()

        # --- Identidades ---
        identity1 = IdentityModel(Student_Identity=None, Teacher_Identity=0, Management_Admin_Identity=1, Schedule="morning")
        identity2 = IdentityModel(Student_Identity=None, Teacher_Identity=2001, Management_Admin_Identity=0, Schedule="evening")
        identity3 = IdentityModel(Student_Identity=22393204, Teacher_Identity=None, Management_Admin_Identity=0, Schedule="evening", Major="Ingeniería en desarrollo biomédico")
        session.add_all([identity1, identity2, identity3])
        session.commit()

        # --- Usuarios ---
        user1 = UserModel(
            User_Name="Guillermo Garcia Canul",
            User_Email="guillermo.jesus.garcia.canul@gmail.com",
            FK_Rol_ID=admin_role.Id,
            Telephone=9983187269,
            FK_Identity_ID=identity1.Id
        )
        user2 = UserModel(
            User_Name="Alisson",
            User_Email="alisson@gmail.com",
            FK_Rol_ID=teacher_role.Id,
            Telephone=9983187269,
            FK_Identity_ID=identity2.Id
        )
        user3 = UserModel(
            User_Name="Aysha Medina Garcia",
            User_Email="aysha_medina_garcia@gmail.com",
            FK_Rol_ID=student_role.Id,
            Telephone=9983187269,
            FK_Identity_ID=identity3.Id
        )
        session.add_all([user1, user2, user3])
        session.commit()

        # --- Tokens ---
        token1 = TokenModel(
            Token="abc123",
            InBlackList=False,
            Date_Expiration_Time=date(2025, 12, 31),
            FK_User_ID=user1.Id
        )
        token2 = TokenModel(
            Token="def456",
            InBlackList=True,
            Date_Expiration_Time=date(2025, 11, 15),
            FK_User_ID=user2.Id
        )
        session.add_all([token1, token2])
        session.commit()

        print("Datos dummy insertados correctamente")

    except Exception as e:
        print("Error durante el seed:", e)
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()
