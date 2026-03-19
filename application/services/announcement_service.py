import os
import uuid
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from application.dtos.contents.announcement_dto import CreateAnnouncementDTO, UpdateAnnouncementDTO
from infrastructure.persistence.models.content_model import ContentModel  # Mantenemos el modelo original

# Configuración de rutas (alineado con el mount estático: app.mount("/contents", ...))
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.normpath(os.path.join(current_dir, "..", ".."))
FORMATS_STORAGE = os.path.join(project_root, "app", "contents", "formats")
ANNOUNCEMENTS_STORAGE = os.path.join(project_root, "app", "contents", "announcements")


def _save_format_file(file: UploadFile) -> str:
    """Guarda el archivo físicamente y retorna la URL pública."""
    os.makedirs(FORMATS_STORAGE, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    disk_path = os.path.join(FORMATS_STORAGE, unique_name)

    content = file.file.read()
    with open(disk_path, "wb") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

    return f"/contents/formats/{unique_name}"


def _del_format_file(url: Optional[str]) -> None:
    """Elimina del disco el archivo referenciado por la URL pública."""
    if not url:
        return

    filename = os.path.basename(url)
    disk_path = os.path.join(FORMATS_STORAGE, filename)
    if os.path.exists(disk_path):
        os.remove(disk_path)


def _save_announcement_image(file: UploadFile) -> str:
    """Guarda una imagen asociada al comunicado y retorna la URL pública."""
    os.makedirs(ANNOUNCEMENTS_STORAGE, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    disk_path = os.path.join(ANNOUNCEMENTS_STORAGE, unique_name)

    content = file.file.read()
    with open(disk_path, "wb") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())

    return f"/contents/announcements/{unique_name}"


def _del_announcement_image(url: Optional[str]) -> None:
    """Elimina del disco la imagen referenciada por la URL pública."""
    if not url:
        return

    filename = os.path.basename(url)
    disk_path = os.path.join(ANNOUNCEMENTS_STORAGE, filename)
    if os.path.exists(disk_path):
        os.remove(disk_path)

def get_all_announcements_service(db: Session) -> List[ContentModel]:
    return db.query(ContentModel).all()

def create_announcement_service(db: Session, data: CreateAnnouncementDTO, file: Optional[UploadFile] = None) -> ContentModel:
    # Convertimos el DTO a diccionario para manipularlo
    content_dict = data.model_dump()
    
    saved_doc_url: Optional[str] = None
    saved_image_url: Optional[str] = None
    if data.Type == "Formato":
        if not file:
            raise ValueError("El archivo es requerido cuando Type es 'Formato'")

        saved_doc_url = _save_format_file(file)
        content_dict["UrlDocument"] = saved_doc_url
        content_dict["IsAnAdvice"] = False
    elif file:
        # Si no es Formato, tratamos el archivo como imagen del comunicado
        saved_image_url = _save_announcement_image(file)
        content_dict["UrlImage"] = saved_image_url

    # En SQL Server `Contents.UrlImage` y `Contents.UrlDocument` son NOT NULL: normalizamos a string vacía
    if content_dict.get("UrlImage") is None:
        content_dict["UrlImage"] = ""
    if content_dict.get("UrlDocument") is None:
        content_dict["UrlDocument"] = ""

    new_item = ContentModel(**content_dict)
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    except Exception:
        db.rollback()
        _del_format_file(saved_doc_url)
        _del_announcement_image(saved_image_url)
        raise

def save_file(file: UploadFile) -> str:
    """Compat: Guarda el archivo y retorna la URL pública."""
    return _save_format_file(file)

def update_announcement_service(db: Session, id: int, data: UpdateAnnouncementDTO) -> ContentModel:
    item = db.query(ContentModel).filter(ContentModel.Id == id).first()
    if not item:
        raise KeyError("Comunicado no encontrado")

    for key, value in data.model_dump(exclude_unset=True).items():
        # Evitamos NULL en columnas NOT NULL
        if key == "UrlImage" and value is None:
            value = ""
        if key == "UrlDocument" and value is None:
            value = ""
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