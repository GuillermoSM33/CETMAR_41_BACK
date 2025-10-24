from typing import Optional
from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class ReportCardRawModel(Base):
    __tablename__ = "report_card_raw"
    __table_args__ = (UniqueConstraint("SHA256", name="uq_rcr_sha256"),)

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Identity_ID: Mapped[int] = mapped_column(Integer, ForeignKey("identities.Id"), nullable=False)
    Periodo: Mapped[str] = mapped_column(String(64), nullable=False)

    Raw_JSON: Mapped[str] = mapped_column(Text, nullable=False)
    SHA256: Mapped[str] = mapped_column(String(64), nullable=False)
    Stored_URI: Mapped[Optional[str]] = mapped_column(String(400), nullable=True)

    Created_At: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.sysdatetime())

    identity = relationship("IdentityModel", back_populates="raw_report_cards")
