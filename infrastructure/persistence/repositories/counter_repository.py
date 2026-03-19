from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import case
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
    def get_students_by_gender(db: Session) -> dict:
        male = db.query(IdentityModel).filter(IdentityModel.Gender == 'M').count()
        female = db.query(IdentityModel).filter(IdentityModel.Gender == 'F').count()
        return {"male": male, "female": female}

    @staticmethod
    def get_students_by_regularity(db: Session) -> dict:
        regular = db.query(IdentityModel).filter(IdentityModel.IsRegular == True).count()
        irregular = db.query(IdentityModel).filter(IdentityModel.IsRegular == False).count()
        return {"regular": regular, "irregular": irregular}

    @staticmethod
    def get_students_by_career(db: Session) -> list:
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
            "students_by_gender": CounterRepository.get_students_by_gender(db),
            "students_by_regularity": CounterRepository.get_students_by_regularity(db),
            "students_by_career": CounterRepository.get_students_by_career(db),
            "registered_users": CounterRepository.get_registered_users_count(db),
            "active_events": CounterRepository.get_active_events_count(db),
            "uploaded_report_cards": CounterRepository.get_uploaded_report_cards_count(db),
        }
    
    @staticmethod
    def get_averages_distribution(db: Session) -> list:
        # Creamos las "cubetas" (rangos) para los promedios
        rango_promedio = case(
            (ReportCardModel.Promedio < 6.0, "Reprobados"),
            (ReportCardModel.Promedio.between(6.0, 7.0), "6.0-7.0"),
            (ReportCardModel.Promedio.between(7.1, 8.0), "7.1-8.0"),
            (ReportCardModel.Promedio.between(8.1, 9.0), "8.1-9.0"),
            (ReportCardModel.Promedio.between(9.1, 10.0), "9.1-10.0"),
            else_="Sin Promedio"
        ).label("rango")

        cte = db.query(
            ReportCardModel.Id,
            rango_promedio
        ).filter(ReportCardModel.Promedio > 0).cte("promedios_cte")

        
        results = db.query(cte.c.rango, func.count(cte.c.Id))\
                    .group_by(cte.c.rango)\
                    .all()

        return [{"rango": r[0], "cantidad": r[1]} for r in results]


    @staticmethod
    def get_leave_dates(db: Session) -> list:
        # Solo traemos el campo de fecha de los que tienen IsLeave = True y la fecha no es nula
        fechas = db.query(IdentityModel.LeaveStartDate)\
                   .filter(IdentityModel.IsLeave == True)\
                   .filter(IdentityModel.LeaveStartDate.isnot(None))\
                   .all()
        
        # Retornamos una lista simple de strings ['2023-08-15', '2023-08-20', ...]
        return [f[0] for f in fechas if f[0]]