from dataclasses import dataclass
from typing import Optional

@dataclass
class ReportCardFilters:
    semestre: Optional[int] = None
    grupo: Optional[str] = None
    estatus: Optional[str] = None
    turno: Optional[str] = None
    carrera: Optional[str] = None
    periodo: Optional[str] = None
    search: Optional[str] = None