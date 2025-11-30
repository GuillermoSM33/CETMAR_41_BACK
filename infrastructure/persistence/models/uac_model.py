from typing import Optional, List
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class UACModel(Base):
    """Minimal catalog for UACs (materias). Keep only the identity and name.
    Additional metadata can be added later if required.
    """

    __tablename__ = "uacs"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Clave: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    Nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    Tipo: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    items: Mapped[List["ReportCardItemModel"]] = relationship("ReportCardItemModel", back_populates="uac")
    raw_entries: Mapped[List["ReportCardRawModel"]] = relationship("ReportCardRawModel", back_populates="uac")

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .report_card_raw_model import ReportCardRawModel
    from .report_card_item_model import ReportCardItemModel
