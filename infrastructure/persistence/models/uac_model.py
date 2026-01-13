from typing import Optional, List
from infrastructure.persistence.models.report_card_item_model import ReportCardItemModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class UACModel(Base):
    __tablename__ = "uacs"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Clave: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    Nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    Tipo: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)    
    Creditos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Horas_Sem: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    items: Mapped[List["ReportCardItemModel"]] = relationship("ReportCardItemModel", back_populates="uac")
