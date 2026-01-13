from pydantic import BaseModel
from typing import Optional

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

class GetStudentDetailDTO(GetStudentDTO):
    
    Matricula: Optional[int] = None 
    Numero_Control: Optional[str] = None 
    CURP: Optional[str] = None
    Grupo: Optional[str] = None
    Carrera: Optional[str] = None
    
    class Config:
        orm_mode = True