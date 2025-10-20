from typing import Protocol
from application.dtos.report_cards.report_card_dto import ReportCardDTO

class IReportCardParser(Protocol):
    def parse(self, file_bytes: bytes) -> ReportCardDTO: ...
