import re, pdfplumber
from typing import List, Optional, BinaryIO
from application.interfaces.report_cards.report_card_parser import IReportCardParser
from application.dtos.report_cards.report_card_dto import ReportCardDTO, UACItemDTO

_header = {
    "curp": re.compile(r"CURP:\s*([A-Z0-9]+)"),
    "alumno": re.compile(r"Nombre del alumno:\s*(.+)"),
    "control": re.compile(r"Número de control:\s*([0-9]+)"),
    "plan": re.compile(r"Plan de estudios:\s*(.+)"),
    "carrera": re.compile(r"Carrera\s*:\s*(.+)"),
    "promedio": re.compile(r"Promedio:\s*([0-9]+(?:\.[0-9]+)?)"),
    # “Avance de UAC … Obligatorias / Optativos / Total” aparecen con tres números
    "avance": re.compile(r"Avance de UAC:.*?Obligatorias.*?(\d+).*?Optativos.*?(\d+).*?Total.*?(\d+)", re.S),
}

# Filas UAC (CETMAR 41 ...). Capturamos columnas separadas por espacios,
# dejando el nombre como bloque "perezoso" hasta la calificación.
_row = re.compile(
    r"CETMAR\s+41\s+(\S+)\s+([0-9A-Z-]+)\s+(\d+)\s+(.+?)\s+"
    r"(NA|[0-9]+(?:\.[0-9]+)?)\s+(\d+)\s*/\s*(\d+|---)\s+(.+?)(?:\n|$)"
)

class LocalReportCardParser(IReportCardParser):
    def parse(self, fp: BinaryIO) -> ReportCardDTO:
        with pdfplumber.open(fp) as pdf:
            text = "\n".join(filter(None, ((p.extract_text() or "") for p in pdf.pages)))

        def _m(rx, default=""):
            m = rx.search(text)
            return m.group(1).strip() if m else default

        curp = _m(_header["curp"])
        alumno = _m(_header["alumno"])
        control = _m(_header["control"])
        plan = _m(_header["plan"])
        carrera = _m(_header["carrera"])
        promedio = float(_m(_header["promedio"], "0"))
        m_av = _header["avance"].search(text)
        a_obl, a_opt, a_tot = (int(m_av.group(i)) for i in (1,2,3)) if m_av else (0,0,0)

        uac: List[UACItemDTO] = []
        for m in _row.finditer(text):
            tipo, clave, semestre, nombre, calif, horas, cred, periodo = m.groups()
            uac.append(UACItemDTO(
                plantel="CETMAR 41",
                tipo_uac=tipo,
                clave_uac=clave,
                semestre=int(semestre),
                nombre=nombre.strip(),
                calif=None if calif == "NA" else float(calif),
                horas_sem=int(horas),
                creditos=None if cred == "---" else int(cred),
                periodo=periodo.strip(),
            ))

        return ReportCardDTO(
            curp=curp, alumno=alumno, numero_control=control,
            plan_estudios=plan, carrera=carrera,
            avance_oblig=a_obl, avance_opt=a_opt, avance_total=a_tot,
            promedio=promedio, uac=uac
        )
