from pydantic import BaseModel

""" Usamos este DTO para editar a los usuarios """

class UpdateUserDTO(BaseModel):
    Id: int
    User_name: str
    User_email: str
    FK_Rol_ID: int
    Telephone: str
    FK_Identity_ID: int

    class Config:
        orm_mode = True