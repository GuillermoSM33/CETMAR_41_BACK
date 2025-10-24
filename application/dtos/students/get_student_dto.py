from pydantic import BaseModel

""" Usamos este DTO para poder obtener los estudiantes """

class GetStudentDTO(BaseModel):
    Id: int
    User_Name: str
    User_Email: str
    FK_Rol_ID: int
    Telephone: int
    FK_Identity_ID: int
      
    class Config:
        orm_mode = True
