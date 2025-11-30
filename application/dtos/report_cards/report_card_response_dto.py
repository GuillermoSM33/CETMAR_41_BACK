from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StoredUACItemDTO(BaseModel):
    clave_uac: str
    semestre: int
    nombre: str
    calif: Optional[float]


class StoredReportCardDTO(BaseModel):
    id: int
    identity_id: int
    curp: Optional[str]
    alumno: Optional[str]
    numero_control: Optional[str]
    src_sha256: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[StoredUACItemDTO]
