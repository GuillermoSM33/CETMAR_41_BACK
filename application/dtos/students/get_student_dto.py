from pydantic import BaseModel

""" Usamos este DTO para poder obtener los estudiantes """

class GetStudentDTO(BaseModel):
    Id: int
