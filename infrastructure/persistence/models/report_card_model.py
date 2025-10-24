from typing import List, Optional
from datetime import datetime
from infrastructure.persistence.models.report_card_item_model import ReportCardItemModel
from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint, Numeric, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class ReportCardModel(Base):
    __tablename__ = "report_cards"
    __table_args__ = (
        UniqueConstraint("Identity_ID", "Periodo", name="uq_report_cards_identity_periodo"),
        Index("ix_report_cards_identity_periodo", "Identity_ID", "Periodo"),
        Index("ix_report_cards_periodo", "Periodo"),
    )

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Identity_ID: Mapped[int] = mapped_column(Integer, ForeignKey("identities.Id"), nullable=False)

    Periodo: Mapped[str] = mapped_column(String(64), nullable=False)        
    Plan_Estudios: Mapped[Optional[str]] = mapped_column(String(120))
    Carrera: Mapped[Optional[str]] = mapped_column(String(150))
    Avance_Oblig: Mapped[int] = mapped_column(Integer, default=0)
    Avance_Opt: Mapped[int] = mapped_column(Integer, default=0)
    Avance_Total: Mapped[int] = mapped_column(Integer, default=0)
    Promedio: Mapped[float] = mapped_column(Numeric(4, 2), default=0)
    Src_SHA256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True) 

    Created_At: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime())
    Updated_At: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime(), onupdate=func.sysdatetime())

    identity = relationship("IdentityModel", back_populates="report_cards")
    items: Mapped[List["ReportCardItemModel"]] = relationship("ReportCardItemModel", back_populates="report_card", cascade="all, delete-orphan")
