from typing import Optional, List

from sqlalchemy import Integer, String, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.report_card_model import ReportCardModel
from infrastructure.persistence.models.report_card_raw_model import ReportCardRawModel
from .base import Base

class IdentityModel(Base):
    __tablename__ = "identities"
    __table_args__ = (
        Index(
            "ux_identities_curp_not_null",
            "CURP",
            unique=True,
            mssql_where=text("CURP IS NOT NULL"),
        ),
    )

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    Student_Control_Number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)

    CURP: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    Full_Name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    Midle_Name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    Last_Name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    Linkage_Identity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Schoolar_Control_Identity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Director_Identity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    Management_Admin_Identity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    Grupo: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    Schedule: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    Major: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    IsRegular: Mapped[Optional[bool]] = mapped_column(nullable=True, default=True)
    IsLeave: Mapped[Optional[bool]] = mapped_column(nullable=True, default=False)
    LeaveStartDate: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    Gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    users: Mapped[List["UserModel"]] = relationship("UserModel", back_populates="identity")
    report_cards: Mapped[List["ReportCardModel"]] = relationship("ReportCardModel", back_populates="identity")
    raw_report_cards: Mapped[List["ReportCardRawModel"]] = relationship("ReportCardRawModel", back_populates="identity")