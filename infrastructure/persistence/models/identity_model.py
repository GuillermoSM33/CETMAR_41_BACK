from typing import Optional, List
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.report_card_model import ReportCardModel
from infrastructure.persistence.models.report_card_raw_model import ReportCardRawModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class IdentityModel(Base):
    __tablename__ = "identities"
    __table_args__ = (
    )

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    Student_Control_Number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    CURP: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    Full_Name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    Student_Identity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Teacher_Identity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Management_Admin_Identity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Grupo: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    Schedule: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    Major: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    users: Mapped[List["UserModel"]] = relationship("UserModel", back_populates="identity")
    report_cards: Mapped[List["ReportCardModel"]] = relationship("ReportCardModel", back_populates="identity")
    raw_report_cards: Mapped[List["ReportCardRawModel"]] = relationship("ReportCardRawModel", back_populates="identity")
