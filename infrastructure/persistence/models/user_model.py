from sqlalchemy import Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class UserModel(Base):
    __tablename__="users"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    User_Name: Mapped[str] = mapped_column(String(80))
    User_Email: Mapped[str] = mapped_column(String(100), unique=True)
    FK_Rol_ID: Mapped[int] = mapped_column(Integer, ForeignKey("roles.Id"))
    Telephone: Mapped[int] = mapped_column(BigInteger)
    FK_Identity_ID: Mapped[int] = mapped_column(Integer, ForeignKey("identities.Id"))

    role = relationship("RoleModel", back_populates="users")
    identity = relationship("IdentityModel", back_populates="users")
    tokens = relationship("TokenModel", back_populates="user")
    califications = relationship("CalificationModel", back_populates="user")