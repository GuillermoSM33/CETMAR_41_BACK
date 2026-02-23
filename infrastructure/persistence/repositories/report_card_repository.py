from sqlalchemy.orm import Session
from sqlalchemy import or_
from infrastructure.persistence.models import (
    ReportCardModel,
    ReportCardItemModel,
    IdentityModel
)
from application.dtos.report_cards.report_card_filters import ReportCardFilters


class ReportCardRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_filtered(self, filters: ReportCardFilters):
        query = self.db.query(ReportCardModel).join(ReportCardModel.identity)

        if filters.carrera:
            query = query.filter(ReportCardModel.Carrera == filters.carrera)

        if filters.periodo:
            query = query.filter(ReportCardModel.Periodo == filters.periodo)

        if filters.grupo:
            query = query.filter(IdentityModel.Grupo == filters.grupo)

        if filters.estatus:
            query = query.filter(IdentityModel.Estatus == filters.estatus)

        if filters.turno:
            query = query.filter(IdentityModel.Turno == filters.turno)

        if filters.search:
            query = query.filter(
                or_(
                    # Buscamos coincidencias en cualquiera de las partes del nombre
                    IdentityModel.Full_Name.ilike(f"%{filters.search}%"),
                    IdentityModel.Midle_Name.ilike(f"%{filters.search}%"),
                    IdentityModel.Last_Name.ilike(f"%{filters.search}%"),
                    # Y también buscamos coincidencias en el número de control
                    IdentityModel.Student_Control_Number.ilike(f"%{filters.search}%")
                )
            )

        if filters.semestre:
            query = query.join(ReportCardModel.items).filter(
                ReportCardItemModel.Semestre == filters.semestre
            ).distinct()

        return query.all()