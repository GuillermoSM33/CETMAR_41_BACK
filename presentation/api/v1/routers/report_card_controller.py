from fastapi import APIRouter, UploadFile, File, Depends
from application.dtos.report_cards.report_card_dto import ReportCardDTO
from application.interfaces.report_cards.report_card_parser import IReportCardParser
from infrastructure.parsers.report_cards.local_report_card_parser import LocalReportCardParser

router = APIRouter()

def get_parser() -> IReportCardParser:
    # En dev: parser local por pdfplumber; en prod podrías inyectar Azure
    return LocalReportCardParser()

@router.post("/parse", response_model=ReportCardDTO)
async def parse_report_card(file: UploadFile = File(...), parser: IReportCardParser = Depends(get_parser)):
    file.file.seek(0)            
    return parser.parse(file.file)

