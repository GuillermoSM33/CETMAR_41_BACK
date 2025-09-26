from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class IdentityModel(Base):
    __tablename__ = "identities"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Student_Identity: Mapped[int] = mapped_column(Integer, nullable=True)
    Teacher_Identity: Mapped[int] = mapped_column(Integer, nullable=True)
    Management_Admin_Identity: Mapped[int] = mapped_column(Integer, nullable=True)
    Schedule: Mapped[str] = mapped_column(String(80), nullable=True)
    Major: Mapped[str] = mapped_column(String(150), nullable=True)

    users = relationship("UserModel", back_populates="identity")
