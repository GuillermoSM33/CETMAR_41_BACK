from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class StoredUACItemDTO(BaseModel):
    clave_uac: str
    semestre: int
    nombre: str
    calif1: Optional[Union[float, str]]
    calif2: Optional[Union[float, str]]
    calif3: Optional[Union[float, str]]
    # attendance
    asis1: Optional[int]
    asis2: Optional[int]
    asis3: Optional[int]
    acreditado: Optional[bool]


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
