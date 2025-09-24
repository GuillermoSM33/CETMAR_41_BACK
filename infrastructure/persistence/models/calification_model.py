from sqlalchemy import Integer, Boolean, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class CalificationModel(Base):
    __tablename__="califications"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    FK_User_ID: Mapped[int] = mapped_column(Integer, ForeignKey("users.Id"))
    Average: Mapped[float] = mapped_column(Float)
    IsApproved: Mapped[bool] = mapped_column(Boolean, default=True)

    user = relationship("UserModel", back_populates="califications")