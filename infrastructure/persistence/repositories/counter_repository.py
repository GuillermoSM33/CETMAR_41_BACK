from sqlalchemy.orm import Session
from sqlalchemy import func
from infrastructure.persistence.models.identity_model import IdentityModel
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.role_model import RoleModel
from infrastructure.persistence.models.report_card_model import ReportCardModel
from infrastructure.persistence.models.report_card_raw_model import ReportCardRawModel
from typing import List, Dict

class CounterRepository:
    @staticmethod
    def get_total_students(db: Session) -> int:
        return db.query(IdentityModel).join(UserModel, UserModel.FK_Identity_ID == IdentityModel.Id)\
    .join(RoleModel, UserModel.FK_Rol_ID == RoleModel.Id)\
    .filter(RoleModel.Role_Name == "Student").distinct(IdentityModel.Id).count()

    @staticmethod
    def get_processed_report_cards_count(db: Session) -> int:
        return db.query(ReportCardModel).count()

    @staticmethod
    def get_institutional_average(db: Session) -> float:
        avg = db.query(func.avg(ReportCardModel.Promedio)).filter(ReportCardModel.Promedio > 0).scalar()
        return float(avg) if avg else 0.0

    @staticmethod
    def get_inactive_students_count(db: Session) -> int:
        return db.query(IdentityModel).filter(IdentityModel.IsLeave == True).count()

    @staticmethod
    def get_male_students_count(db: Session) -> int:
        return db.query(IdentityModel).filter(IdentityModel.Gender == 'M').count()

    @staticmethod
    def get_female_students_count(db: Session) -> int:
        return db.query(IdentityModel).filter(IdentityModel.Gender == 'F').count()

    @staticmethod
    def get_regular_students_count(db: Session) -> int:
        return db.query(IdentityModel).filter(IdentityModel.IsRegular == True).count()

    @staticmethod
    def get_irregular_students_count(db: Session) -> int:
        return db.query(IdentityModel).filter(IdentityModel.IsRegular == False).count()

    @staticmethod
    def get_students_by_career(db: Session) -> List[Dict]:
        results = db.query(IdentityModel.Major, func.count(IdentityModel.Id)).group_by(IdentityModel.Major).all()
        return [{"major": r[0], "count": r[1]} for r in results]

    @staticmethod
    def get_registered_users_count(db: Session) -> int:
        return db.query(UserModel).join(RoleModel, UserModel.FK_Rol_ID == RoleModel.Id).filter(RoleModel.Role_Name != "Student").count()

    @staticmethod
    def get_active_events_count(db: Session) -> int:
        # No hay modelo de eventos, retorna 0
        return 0

    @staticmethod
    def get_uploaded_report_cards_count(db: Session) -> int:
        return db.query(ReportCardRawModel).count()

    @staticmethod
    def get_all_counters(db: Session) -> dict:
        return {
            "total_students": CounterRepository.get_total_students(db),
            "processed_report_cards": CounterRepository.get_processed_report_cards_count(db),
            "institutional_average": CounterRepository.get_institutional_average(db),
            "inactive_students": CounterRepository.get_inactive_students_count(db),
            "male_students": CounterRepository.get_male_students_count(db),
            "female_students": CounterRepository.get_female_students_count(db),
            "regular_students": CounterRepository.get_regular_students_count(db),
            "irregular_students": CounterRepository.get_irregular_students_count(db),
            "students_by_career": CounterRepository.get_students_by_career(db),
            "registered_users": CounterRepository.get_registered_users_count(db),
            "active_events": CounterRepository.get_active_events_count(db),
            "uploaded_report_cards": CounterRepository.get_uploaded_report_cards_count(db),
        }
