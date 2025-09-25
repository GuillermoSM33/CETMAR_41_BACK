from pydantic import BaseModel

""" Usamos este DTO para poder pintar los usuarios sin exponer datos sensibles"""

class GetUserDTO(BaseModel):
    Id: int
    User_Name: str
    User_Email: str
    Telephone: int

    class Config:
        orm_mode = True
