from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
import hashlib

from application.dtos.report_cards.report_card_dto import ReportCardDTO
from application.dtos.report_cards.report_card_filters import ReportCardFilters 
from application.dtos.report_cards.report_card_response_dto import StoredReportCardDTO, StoredUACItemDTO
from application.interfaces.report_cards.report_card_parser import IReportCardParser
from infrastructure.parsers.report_cards.local_report_card_parser import LocalReportCardParser
from infrastructure.persistence.repositories.db import get_db
from infrastructure.persistence.models.report_card_model import ReportCardModel
from application.services.report_card_service import save_parsed_report_cards, get_stored_report_card, get_report
from application.services.report_card_filters_service import ReportCardService
import io

router = APIRouter()

def get_parser() -> IReportCardParser:
    # Inyección simple; en prod podrías cambiar a Azure/otro backend
    return LocalReportCardParser()

@router.get("/")
def get_report_cards(
    semestre: Optional[int] = None,
    grupo: Optional[str] = None,
    estatus: Optional[str] = None,
    turno: Optional[str] = None,
    carrera: Optional[str] = None,
    periodo: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    filters = ReportCardFilters(
        semestre=semestre,
        grupo=grupo,
        estatus=estatus,
        turno=turno,
        carrera=carrera,
        periodo=periodo,
        search=search,
    )

    service = ReportCardService(db)
    return service.get_report_cards(filters)

@router.post("/parse_many", response_model=List[StoredReportCardDTO])
async def parse_report_card_many(
    files: List[UploadFile] = File(...),
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
        # Obtener la ruta del archivo desde el servicio
        file_path = get_report(control_number)
        
        if not file_path:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró ninguna boleta para el número de control: {control_number}. "
                       f"Asegúrate de que el documento haya sido procesado previamente."
            )

        # Retornar el archivo PDF
        # media_type='application/pdf' permite que se abra en el visor del navegador
        return FileResponse(
            path=file_path,
            media_type='application/pdf',
            filename=f"Boleta_{control_number}.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en la descarga del archivo: {e}")
        raise HTTPException(status_code=500, detail="Error interno al intentar recuperar el archivo.")