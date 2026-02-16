from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class StoredUACItemDTO(BaseModel):
    clave_uac: str
    semestre: int
    nombre: str
    # Optional enrichment fields from UAC/boleta context
    tipo_uac: Optional[str] = None
    calif: Optional[float] = None
    horas_sem: Optional[int] = None
    creditos: Optional[int] = None
    periodo: Optional[str] = None

    # Per-period values stored in report_card_items
    calif1: Optional[Union[float, str]] = None
    calif2: Optional[Union[float, str]] = None
    calif3: Optional[Union[float, str]] = None
    asis1: Optional[int] = None
    asis2: Optional[int] = None
    asis3: Optional[int] = None
    acreditado: Optional[bool] = None


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
