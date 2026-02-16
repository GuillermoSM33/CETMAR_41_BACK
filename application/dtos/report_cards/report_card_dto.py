from pydantic import BaseModel
from typing import List, Optional, Union

class UACItemDTO(BaseModel):
    plantel: str
    clave_uac: str
    semestre: int
    nombre: str
    # Per-period grades (may be numeric or codes like 'AC'/'NA')
    calif1: Optional[Union[float, str]]
    calif2: Optional[Union[float, str]]
    calif3: Optional[Union[float, str]]

    # Per-period attendance (numeric counts as ints or strings)
    asis1: Optional[Union[int, str]]
    asis2: Optional[Union[int, str]]
    asis3: Optional[Union[int, str]]

    # Derived accreditation: True if accredited, False if not, else None
    acreditado: Optional[bool]

class ReportCardDTO(BaseModel):
    periodo: str
    turno: str
    grupo: str
    plantel: str
    clave_ct: str
    curp: str
    alumno: str
    numero_control: str
    plan_estudios: str
    carrera: str
    generacion: Optional[str] = None
    modalidad: Optional[str] = None
    semestre: Optional[int] = None
    avance_oblig: int
    avance_opt: int
    avance_total: int
    promedio: float
    uac: List[UACItemDTO]

