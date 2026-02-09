import os
import uuid
from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import List, Optional
from infrastructure.persistence.models.content_pages_model import ContentPagesModel
from application.dtos.contents.content_pages_dto import CreateContentPageDTO, UpdateContentPageDTO

# Configuración de rutas
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.normpath(os.path.join(current_dir, "..", "..")) 
STORAGE = os.path.join(project_root, "app", "contents")

def _save_file(file: UploadFile, name: str) -> str:
    """Crea el directorio si no existe y guarda el archivo físicamente"""
    if not os.path.exists(STORAGE):
        os.makedirs(STORAGE, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1]
    fname = f"{name}{ext}"
    path = os.path.join(STORAGE, fname)
    
    content = file.file.read()
    with open(path, "wb") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    
    return f"/contents/{fname}"

def _del_file(url: Optional[str]):
    """Elimina el archivo del disco"""
    if url:
        filename = os.path.basename(url)
        path = os.path.join(STORAGE, filename)
        if os.path.exists(path):
            os.remove(path)

def get_all_pages_content_service(db: Session) -> List[ContentPagesModel]:
    return db.query(ContentPagesModel).all()

def create_page_content_service(db: Session, data: CreateContentPageDTO, file: Optional[UploadFile]) -> ContentPagesModel:
    content_dict = data.model_dump()
    
    # Si hay archivo, generamos la URL ANTES de crear el modelo
    if file:
        unique_id = uuid.uuid4().hex[:8]
        dynamic_name = f"{unique_id}_{os.path.splitext(file.filename)[0]}"
        content_dict["UrlImage"] = _save_file(file, dynamic_name)
    else:
        content_dict["UrlImage"] = None

    new_page_content = ContentPagesModel(**content_dict)
    
    try:
        db.add(new_page_content)
        db.commit() 
        db.refresh(new_page_content)
        return new_page_content
    except Exception as e:
        db.rollback()
        # Si falló la base de datos, limpiamos el archivo físico para no dejar basura
        if file and "UrlImage" in content_dict:
            _del_file(content_dict["UrlImage"])
        raise e

def update_page_content_service(db: Session, page_id: int, data: UpdateContentPageDTO, file: Optional[UploadFile]) -> ContentPagesModel:
    page_content = db.query(ContentPagesModel).filter(ContentPagesModel.Id == page_id).first()
    if not page_content:
        raise KeyError("Contenido de página no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(page_content, key, value)

    # Manejo de archivo nuevo
    old_image_url = None
    if file:
        # Guardamos la referencia de la imagen anterior para borrarla solo si el commit es exitoso
        old_image_url = page_content.UrlImage
        
        # Generamos nuevo nombre único con UUID
        unique_id = uuid.uuid4().hex[:8]
        dynamic_name = f"{unique_id}_{os.path.splitext(file.filename)[0]}"
        
        # Guardamos el nuevo archivo físicamente
        page_content.UrlImage = _save_file(file, dynamic_name)

    try:
        db.commit()
        if old_image_url:
            _del_file(old_image_url)
            
        db.refresh(page_content)
        return page_content
    except Exception as e:
        db.rollback()
        if file:
            _del_file(page_content.UrlImage)
        raise e

def delete_page_content_service(db: Session, page_id: int) -> bool:
    page_content = db.query(ContentPagesModel).filter(ContentPagesModel.Id == page_id).first()
    if page_content:
        _del_file(page_content.UrlImage)
        db.delete(page_content)
        db.commit()
        return True
    return False