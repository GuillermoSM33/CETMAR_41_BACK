from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from infrastructure.persistence.repositories.db import get_db
from application.dtos.contents.announcement_dto import GetAnnouncementDTO, CreateAnnouncementDTO, UpdateAnnouncementDTO
from application.services.announcement_service import (
    get_all_announcements_service,
    create_announcement_service,
    update_announcement_service,
    toggle_announcement_status_service
)

router = APIRouter()

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
    file: Optional[UploadFile] = File(None), # El archivo es opcional
    db: Session = Depends(get_db)
):
    try:
        # Reconstruimos el DTO para validar los datos
        data = CreateAnnouncementDTO(
            Titule=Titule,
            Description=Description,
            Type=Type,
            IsAnAdvice=IsAnAdvice,
            EndDate=EndDate,
            CreationDate=date.today()
        )
        return create_announcement_service(db, data, file)
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