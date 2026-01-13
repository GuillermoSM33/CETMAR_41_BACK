from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List
from sqlalchemy.orm import Session, joinedload
import hashlib

from application.dtos.report_cards.report_card_dto import ReportCardDTO
from application.dtos.report_cards.report_card_response_dto import StoredReportCardDTO, StoredUACItemDTO
from application.interfaces.report_cards.report_card_parser import IReportCardParser
from infrastructure.parsers.report_cards.local_report_card_parser import LocalReportCardParser
from infrastructure.persistence.repositories.db import get_db
from infrastructure.persistence.models.report_card_model import ReportCardModel
from application.services.report_card_service import save_parsed_report_cards, get_stored_report_card

router = APIRouter()

def get_parser() -> IReportCardParser:
    # Inyección simple; en prod podrías cambiar a Azure/otro backend
    return LocalReportCardParser()

@router.post("/parse_many", response_model=List[StoredReportCardDTO])
async def parse_report_card_many(
    file: UploadFile = File(...),
    parser: IReportCardParser = Depends(get_parser),
    db: Session = Depends(get_db),
):
    all_saved_results = []

    for file in files:
        try:
            # Leer contenido de forma asíncrona
            content = await file.read()
            if not content:
                continue
                
            sha256 = hashlib.sha256(content).hexdigest()
            
            # Resetear stream para el parser
            pdf_stream = io.BytesIO(content)
            results = parser.parse_many(pdf_stream)

            if not results:
                print(f"No se detectaron alumnos en el archivo: {file.filename}")
                continue

            # Se envuelven errores específicos del servicio para no detener el lote
            try:
                saved = save_parsed_report_cards(db, results, sha256, content)
                all_saved_results.extend(saved)
            except Exception as e:
                print(f"Error guardando datos de {file.filename}: {e}")
                
        except Exception as e:
            print(f"Error procesando PDF {file.filename}: {e}")
            continue # Pasar al siguiente archivo del lote

    if not all_saved_results:
        raise HTTPException(status_code=422, detail="No se pudo procesar ningún documento del lote.")

    return all_saved_results


@router.get("/{report_card_id}", response_model=StoredReportCardDTO)
def get_report_card(report_card_id: int, db: Session = Depends(get_db)):
    try:
        dto = get_stored_report_card(db, report_card_id)
        return dto
    except KeyError:
        raise HTTPException(status_code=404, detail="Report card no encontrada")
    
@router.get("/download/{control_number}")
async def download_report_card(control_number: str):
    """
    Endpoint para que el estudiante descargue su boleta sellada mediante su número de control.
    """
    try:
        file.file.seek(0)
        content = file.file.read()
        sha256 = hashlib.sha256(content).hexdigest()
        file.file.seek(0)

        results = parser.parse_many(file.file)
        if not results:
            raise HTTPException(status_code=422, detail="No se detectó ningún alumno en el PDF.")
        try:
            saved = save_parsed_report_cards(db, results, sha256)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error guardando boletas: {e}")

        return saved
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar PDF: {e}")


@router.get("/{report_card_id}", response_model=StoredReportCardDTO)
def get_report_card(report_card_id: int, db: Session = Depends(get_db)):
    try:
        dto = get_stored_report_card(db, report_card_id)
        return dto
    except KeyError:
        raise HTTPException(status_code=404, detail="Report card no encontrada")
