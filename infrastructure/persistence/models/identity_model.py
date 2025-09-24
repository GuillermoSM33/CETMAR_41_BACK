from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class IdentityModel(Base):
    __tablename__ = "identities"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Student_Identity: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)
    Teacher_Identity: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)

    users = relationship("UserModel", back_populates="identity")
