from sqlalchemy import Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class TokenModel(Base):
    __tablename__="tokens"

    Id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Token: Mapped[str] = mapped_column(String(400), unique=True)
    InBlackList: Mapped[bool] = mapped_column(Boolean, default=False)
    FK_User_ID: Mapped[int] = mapped_column(Integer, ForeignKey("users.Id"))
    Date_Expiration_Time: Mapped[Date] = mapped_column(Date)

    user = relationship("UserModel", back_populates="tokens")