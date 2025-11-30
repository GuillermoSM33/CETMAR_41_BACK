from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class ReportCardItemModel(Base):
    """Simplified report_card_items model that stores summarized per-materia
    entries when needed by the application. Kept minimal to match boleta fields.
    """

    __tablename__ = "report_card_items"
    __table_args__ = (
        UniqueConstraint("ReportCard_ID", "Clave_UAC", "Semestre", name="uq_rci_rc_clave_sem"),
        Index("ix_rci_reportcard", "ReportCard_ID"),
    )

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ReportCard_ID: Mapped[int] = mapped_column(Integer, ForeignKey("report_cards.Id"), nullable=False)

    UAC_ID: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("uacs.Id"), nullable=True)
    Clave_UAC: Mapped[str] = mapped_column(String(32), nullable=False)
    Semestre: Mapped[int] = mapped_column(Integer, nullable=False)
    Nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    Calificacion: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)

    report_card = relationship("ReportCardModel", back_populates="items")
    uac = relationship("UACModel", back_populates="items")
    raw_entries: Mapped[List["ReportCardRawModel"]] = relationship("ReportCardRawModel", back_populates="report_card_item")


if TYPE_CHECKING:
    from .report_card_raw_model import ReportCardRawModel
