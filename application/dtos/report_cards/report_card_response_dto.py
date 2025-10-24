from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StoredUACItemDTO(BaseModel):
    clave_uac: str
    semestre: int
    nombre: str
    tipo_uac: Optional[str]
    calif: Optional[float]
    horas_sem: Optional[int]
    creditos: Optional[int]
    periodo: Optional[str]


class StoredReportCardDTO(BaseModel):
    id: int
    identity_id: int
    curp: Optional[str]
    alumno: Optional[str]
    numero_control: Optional[str]
    periodo: str
    plan_estudios: Optional[str]
    carrera: Optional[str]
    avance_oblig: int
    avance_opt: int
    avance_total: int
    promedio: float
    src_sha256: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[StoredUACItemDTO]
