from sqlalchemy.orm import Session
from infrastructure.persistence.models.content_model import ContentModel # Mantenemos el modelo original
from application.dtos.contents.announcement_dto import CreateAnnouncementDTO, UpdateAnnouncementDTO
from typing import List, Optional
from fastapi import UploadFile
import os 
import uuid

UPLOAD_DIR = "app/contents/formats"
# Aseguramos que la carpeta exista al arrancar
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_all_announcements_service(db: Session) -> List[ContentModel]:
    return db.query(ContentModel).all()

def create_announcement_service(db: Session, data: CreateAnnouncementDTO, file: Optional[UploadFile] = None) -> ContentModel:
    # Convertimos el DTO a diccionario para manipularlo
    content_dict = data.model_dump()
    
    if data.Type == "Formato" and file:
        # Generamos nombre único
        file_extension = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        
        # Guardamos físicamente el archivo
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        
        content_dict["UrlDocument"] = file_path
        content_dict["IsAnAdvice"] = False 
    
    if content_dict.get("UrlImage") is None:
        content_dict["UrlImage"] = ""

    new_item = ContentModel(**content_dict)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item

def save_file(file: UploadFile) -> str:
    """Guarda el archivo y retorna la ruta relativa"""
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
        
    return file_path

def update_announcement_service(db: Session, id: int, data: UpdateAnnouncementDTO) -> ContentModel:
    item = db.query(ContentModel).filter(ContentModel.Id == id).first()
    if not item:
        raise KeyError("Comunicado no encontrado")

    for key, value in data.model_dump().items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

def toggle_announcement_status_service(db: Session, id: int) -> ContentModel:
    """Invierte el estado de IsActive (si es True pasa a False y viceversa)"""
    item = db.query(ContentModel).filter(ContentModel.Id == id).first()
    if not item:
        return None
    
    item.IsActive = not item.IsActive
    db.commit()
    db.refresh(item)
    return item