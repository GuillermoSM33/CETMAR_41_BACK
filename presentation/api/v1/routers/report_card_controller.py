# presentation/api/v1/routers/report_card_controller.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from application.dtos.report_cards.report_card_dto import ReportCardDTO
from application.interfaces.report_cards.report_card_parser import IReportCardParser
from infrastructure.parsers.report_cards.local_report_card_parser import LocalReportCardParser

router = APIRouter()

def get_parser() -> IReportCardParser:
    # Inyección simple; en prod podrías cambiar a Azure/otro backend
    return LocalReportCardParser()

@router.post("/parse_many", response_model=List[ReportCardDTO])
async def parse_report_card_many(
    file: UploadFile = File(...),
    parser: IReportCardParser = Depends(get_parser)
):
    try:
        file.file.seek(0)
        results = parser.parse_many(file.file)
        if not results:
            raise HTTPException(status_code=422, detail="No se detectó ningún alumno en el PDF.")
        return results
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar PDF: {e}")
