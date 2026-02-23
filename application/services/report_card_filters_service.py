from sqlalchemy.orm import Session
from application.dtos.report_cards.report_card_filters import ReportCardFilters
from infrastructure.persistence.repositories.report_card_repository import ReportCardRepository


class ReportCardService:

    def __init__(self, db: Session):
        self.repo = ReportCardRepository(db)

    def get_report_cards(self, filters: ReportCardFilters):
        return self.repo.get_filtered(filters)