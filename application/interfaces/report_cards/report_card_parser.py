from typing import Protocol, List, BinaryIO
from application.dtos.report_cards.report_card_dto import ReportCardDTO

class IReportCardParser(Protocol):
    def parse_many(self, fp: BinaryIO) -> List[ReportCardDTO]: ...
