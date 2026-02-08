from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List  # <--- IMPORTANTE: Esto soluciona tu error

from infrastructure.persistence.repositories.db import get_db
from application.dtos.contents.content_dto import GetContentDTO, CreateContentDTO, UpdateContentDTO
from application.services.content_service import (
    get_all_contents_service, 
    create_content_service, 
    update_content_service, 
    disable_content_service, 
    enable_content_service
)

router = APIRouter()

# --- OBTENER TODOS ---
@router.get("/", response_model=List[GetContentDTO])
def get_contents(db: Session = Depends(get_db)):
    return get_all_contents_service(db)

# --- CREAR ---
@router.post("/", response_model=GetContentDTO)
def create_content(content_data: CreateContentDTO, db: Session = Depends(get_db)):
    try:
        return create_content_service(db, content_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al crear: {str(e)}")

# --- ACTUALIZAR ---
@router.put("/{content_id}", response_model=GetContentDTO)
def update_content(content_id: int, content_data: UpdateContentDTO, db: Session = Depends(get_db)):
    try:
        return update_content_service(db, content_id, content_data)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al actualizar: {str(e)}")

# --- DESACTIVAR (Borrado Lógico) ---
@router.patch("/{content_id}/disable")
def disable_content(content_id: int, db: Session = Depends(get_db)):
    if not disable_content_service(db, content_id):
        raise HTTPException(status_code=404, detail="No se encontró el contenido para desactivar")
    return {"message": "Contenido desactivado correctamente"}

# --- ACTIVAR (Revertir Borrado) ---
@router.patch("/{content_id}/enable")
def enable_content(content_id: int, db: Session = Depends(get_db)):
    if not enable_content_service(db, content_id):
        raise HTTPException(status_code=404, detail="No se encontró el contenido para activar")
    return {"message": "Contenido activado correctamente"}