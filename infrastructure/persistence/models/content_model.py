from sqlalchemy import Date, Integer, Boolean, String, Date
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class ContentModel(Base):
    __tablename__="Contents"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Description: Mapped[str] = mapped_column(String)
    Titule: Mapped[str] = mapped_column(String)
    Type: Mapped[str] = mapped_column(String)
    UrlImage: Mapped[str] = mapped_column(String, default=None)
    UrlDocument: Mapped[str] = mapped_column(String, default=None)
    IsAnAdvice: Mapped[bool] = mapped_column(Boolean, default=False)
    CreationDate: Mapped[Date] = mapped_column(Date, nullable=True)
    EndDate: Mapped[Date] = mapped_column(Date, nullable=True)
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True)