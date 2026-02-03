from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class ContentPagesModel(Base):
    __tablename__="content_pages"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Description: Mapped[str] = mapped_column(String, nullable=True)
    Titule: Mapped[str] = mapped_column(String, nullable=True)
    UrlImage: Mapped[str] = mapped_column(String, default=None)
    Page: Mapped[str] = mapped_column(String, nullable=True)
    ComponentPage: Mapped[str] = mapped_column(String, nullable=True)
