from typing import Optional
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
    # Per-period grades: store as short strings to allow 'AC'/'NA' or numeric values
    Calificacion1: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    Calificacion2: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    Calificacion3: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    # Attendance values (store numeric counts)
    Asistencia1: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Asistencia2: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Asistencia3: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Convenience: legacy single final grade
    Calificacion: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)

    report_card = relationship("ReportCardModel", back_populates="items")
    uac = relationship("UACModel", back_populates="items")
