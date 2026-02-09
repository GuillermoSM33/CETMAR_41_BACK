from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from infrastructure.persistence.repositories.db import get_db
from application.dtos.contents.content_pages_dto import GetContentPageDTO, CreateContentPageDTO, UpdateContentPageDTO
from application.services.content_page_service import (
    get_all_pages_content_service,
    create_page_content_service,
    update_page_content_service,
    delete_page_content_service
)

router = APIRouter()

@router.get("/", response_model=List[GetContentPageDTO])
def get_all_pages(db: Session = Depends(get_db)):
    return get_all_pages_content_service(db)

@router.post("/", response_model=GetContentPageDTO)
async def create_page(
    Titule: Optional[str] = Form(None),
    Description: Optional[str] = Form(None),
    Page: Optional[str] = Form(None),
    ComponentPage: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        # Mapeamos los campos del Form al DTO
        data = CreateContentPageDTO(
            Titule=Titule,
            Description=Description,
            Page=Page,
            ComponentPage=ComponentPage
        )
        return create_page_content_service(db, data, image)
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error al registrar el contenido de página: {str(e)}"
        )

@router.put("/{page_id}", response_model=GetContentPageDTO)
async def update_page(
    page_id: int,
    Titule: Optional[str] = Form(None),
    Description: Optional[str] = Form(None),
    Page: Optional[str] = Form(None),
    ComponentPage: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        # Mapeamos los campos del Form al DTO de actualización
        data = UpdateContentPageDTO(
            Titule=Titule,
            Description=Description,
            Page=Page,
            ComponentPage=ComponentPage
        )
        return update_page_content_service(db, page_id, data, image)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Error al actualizar el contenido de página: {str(e)}"
        )

@router.delete("/{page_id}")
def delete_page(page_id: int, db: Session = Depends(get_db)):
    try:
        success = delete_page_content_service(db, page_id)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="No se encontró el contenido para eliminar"
            )
        return {"message": "Contenido y archivo físico eliminados correctamente"}
    except HTTPException as http_e:
        raise http_e
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno al intentar eliminar el registro: {str(e)}"
        )