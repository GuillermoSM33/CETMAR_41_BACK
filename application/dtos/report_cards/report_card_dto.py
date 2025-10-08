from pydantic import BaseModel
from typing import List, Optional

class UACItemDTO(BaseModel):
    plantel: str
    tipo_uac: str
    clave_uac: str
    semestre: int
    nombre: str
    calif: Optional[float]  
    horas_sem: int
    creditos: Optional[int] 
    periodo: str            

class ReportCardDTO(BaseModel):
    curp: str
    alumno: str
    numero_control: str
    plan_estudios: str
    carrera: str
    avance_oblig: int
    avance_opt: int
    avance_total: int
    promedio: float
    uac: List[UACItemDTO]
