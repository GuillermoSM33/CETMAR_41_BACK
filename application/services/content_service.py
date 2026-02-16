from sqlalchemy.orm import Session
from infrastructure.persistence.models.content_model import ContentModel
from application.dtos.contents.content_dto import CreateContentDTO, UpdateContentDTO
from typing import List

def get_all_contents_service(db: Session) -> List[ContentModel]:
    # Retornamos todos (activos e inactivos) para que el admin pueda ver qué reactivar
    return db.query(ContentModel).all()

def create_content_service(db: Session, content_data: CreateContentDTO) -> ContentModel:
    new_content = ContentModel(**content_data.model_dump())
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content

def update_content_service(db: Session, content_id: int, content_data: UpdateContentDTO) -> ContentModel:
    content = db.query(ContentModel).filter(ContentModel.Id == content_id).first()
    if not content:
        raise KeyError("Contenido no encontrado")

    # El iterador: mapea dinámicamente cada campo del DTO al Modelo
    for key, value in content_data.model_dump().items():
        setattr(content, key, value)

    db.commit()
    db.refresh(content)
    return content

def disable_content_service(db: Session, content_id: int) -> bool:
    """Baja lógica"""
    content = db.query(ContentModel).filter(ContentModel.Id == content_id).first()
    if content:
        content.IsActive = False
        db.commit()
        return True
    return False

def enable_content_service(db: Session, content_id: int) -> bool:
    """Reactivar contenido"""
    content = db.query(ContentModel).filter(ContentModel.Id == content_id).first()
    if content:
        content.IsActive = True
        db.commit()
        return True
    return False