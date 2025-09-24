from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class RoleModel(Base):
    __tablename__ = "roles"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Role_Name: Mapped[str] = mapped_column(String(50))

    users = relationship("UserModel", back_populates="role")