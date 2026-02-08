from pydantic import BaseModel

""" Usamos este DTO para crear usuarios nuevos"""

class CreateUserDTO(BaseModel):
    User_Name: str
    User_Email: str
    Telephone: int
    Linkage_Identity: int
    Management_Admin_Identity: int
    Schedule: str
    Major: str
    Student_Control_Number: str
    CURP: str
    Full_Name: str
    Grupo: str
    Schoolar_Control_Identity: int
    Director_Identity: int
    FK_Rol_ID: int

    class Config:
        orm_mode = True