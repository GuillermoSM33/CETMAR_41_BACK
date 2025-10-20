from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class AuthModel(Base):
    __tablename__ = "passwords"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    FK_User_ID: Mapped[int] = mapped_column(Integer, ForeignKey("users.Id"), unique=True)
    Hashed_Password: Mapped[str] = mapped_column(String(255))

    user = relationship("UserModel", back_populates="auth")
