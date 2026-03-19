from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from datetime import date, datetime
from infrastructure.persistence.repositories.db import get_db
from application.dtos.contents.announcement_dto import GetAnnouncementDTO, CreateAnnouncementDTO, UpdateAnnouncementDTO
from application.services.announcement_service import (
    get_all_announcements_service,
    create_announcement_service,
    update_announcement_service,
    toggle_announcement_status_service
)

router = APIRouter()


def _parse_date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None

    text = value.strip()
    if not text:
        return None

    # Aceptamos formatos típicos del front: ISO y dd-mm-yy / dd-mm-yyyy
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d-%m-%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    raise ValueError("EndDate debe ser una fecha válida (YYYY-MM-DD o DD-MM-YY/DD-MM-YYYY)")

@router.get("", response_model=List[GetAnnouncementDTO])
def get_announcements(db: Session = Depends(get_db)):
    return get_all_announcements_service(db)

@router.post("", response_model=GetAnnouncementDTO)
def create_announcement(
    Titule: str = Form(...),
    Description: str = Form(...),
    Type: str = Form(...),
    IsAnAdvice: bool = Form(True),
    EndDate: Optional[str] = Form(None),
    file: Union[UploadFile, str, None] = File(None),  # algunos frontends mandan "" cuando no hay archivo
    db: Session = Depends(get_db)
):
    try:
        # Normalizamos el archivo: si viene como string vacío, lo tratamos como None
        normalized_file: Optional[UploadFile]
        if isinstance(file, str):
            if not file.strip():
                normalized_file = None
            else:
                raise ValueError("El campo 'file' debe enviarse como archivo (multipart), no como texto")
        else:
            normalized_file = file

        parsed_end_date = _parse_date(EndDate)

        # Reconstruimos el DTO para validar los datos
        data = CreateAnnouncementDTO(
            Titule=Titule,
            Description=Description,
            Type=Type,
            IsAnAdvice=IsAnAdvice,
            EndDate=parsed_end_date,
            CreationDate=date.today()
        )
        return create_announcement_service(db, data, normalized_file)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=GetAnnouncementDTO)
def update_announcement(id: int, data: UpdateAnnouncementDTO, db: Session = Depends(get_db)):
    try:
        return update_announcement_service(db, id, data)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{id}/toggle", response_model=GetAnnouncementDTO)
def toggle_status(id: int, db: Session = Depends(get_db)):
    updated_item = toggle_announcement_status_service(db, id)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Comunicado no encontrado")
    return updated_item