from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint, Text, func, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class ReportCardRawModel(Base):
    """Minimal model to store a single UAC (materia) extracted from a boleta.

    Kept fields are intentionally small: identity link, optional fks to item/uac,
    clave, semestre, nombre, calificacion, raw JSON and SHA256 for dedup.
    """

    __tablename__ = "report_card_raw"
    __table_args__ = (
        UniqueConstraint("SHA256", name="uq_rcr_sha256"),
        Index("ix_rcr_identity_clave", "Identity_ID", "Clave_UAC"),
    )

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Identity_ID: Mapped[int] = mapped_column(Integer, ForeignKey("identities.Id"), nullable=False)

    # Optional links kept for cross-referencing; nullable to allow gradual backfill
    ReportCard_Item_ID: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("report_card_items.Id"), nullable=True)
    UAC_ID: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("uacs.Id"), nullable=True)

    Clave_UAC: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    Semestre: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    Calificacion: Mapped[Optional[float]] = mapped_column(Numeric(4, 2), nullable=True)

    Raw_JSON: Mapped[str] = mapped_column(Text, nullable=False)
    SHA256: Mapped[str] = mapped_column(String(64), nullable=False)

    Created_At: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime())

    # Relationships (keep backrefs for convenience elsewhere in the codebase)
    identity = relationship("IdentityModel", back_populates="raw_report_cards")
    report_card_item = relationship("ReportCardItemModel", back_populates="raw_entries")
    uac = relationship("UACModel", back_populates="raw_entries")
