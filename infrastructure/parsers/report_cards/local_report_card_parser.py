# infrastructure/parsers/report_cards/local_report_card_parser.py
import re, pdfplumber
from typing import List, BinaryIO
from application.dtos.report_cards.report_card_dto import ReportCardDTO, UACItemDTO
from application.interfaces.report_cards.report_card_parser import IReportCardParser

_header = {
    "curp": re.compile(r"CURP:\s*([A-Z0-9]+)"),
    "alumno": re.compile(r"Nombre del alumno:\s*(.+)"),
    "control": re.compile(r"Número de control:\s*([0-9]+)"),
    "plan": re.compile(r"Plan de estudios:\s*(.+)"),
    "carrera": re.compile(r"Carrera\s*:\s*(.+)"),
    "promedio": re.compile(r"Promedio:\s*([0-9]+(?:\.[0-9]+)?)"),
    "avance": re.compile(
        r"Avance de UAC:.*?Obligatorias.*?(\d+).*?Optativos.*?(\d+).*?Total.*?(\d+)",
        re.S,
    ),
}

# Relaja el plantel para no fijarlo a 41
_row = re.compile(
    r"CETMAR\s+\d+\s+(\S+)\s+([0-9A-Z-]+)\s+(\d+)\s+(.+?)\s+"
    r"(NA|[0-9]+(?:\.[0-9]+)?)\s+(\d+)\s*/\s*(\d+|---)\s+(.+?)(?:\n|$)"
)

class LocalReportCardParser(IReportCardParser):
    def parse_many(self, fp: BinaryIO) -> List[ReportCardDTO]:
        # Asegura inicio
        try:
            fp.seek(0)
        except Exception:
            pass

        with pdfplumber.open(fp) as pdf:
            full = "\n".join(filter(None, ((p.extract_text() or "") for p in pdf.pages)))

        # HISTORIAL ACADEMICO 
        split_rx = re.compile(r"(?=HISTORIAL\s+ACAD(?:É|E)MICO)", re.I)
        parts = [c for c in split_rx.split(full) if c.strip()]

        # Fallback: si no hubo split pero hay contenido, intenta procesarlo como un solo alumno
        if not parts and full.strip():
            parts = [full]

        def _m(rx: re.Pattern, text: str, default: str = "") -> str:
            m = rx.search(text)
            return m.group(1).strip() if m else default

        results: List[ReportCardDTO] = []

        for text in parts:
            # Rechaza chunks que no parezcan encabezado de alumno
            if "CURP:" not in text and "Nombre del alumno:" not in text:
                continue

            curp     = _m(_header["curp"], text)
            alumno   = _m(_header["alumno"], text)
            control  = _m(_header["control"], text)
            plan     = _m(_header["plan"], text)
            carrera  = _m(_header["carrera"], text)
            promedio = float(_m(_header["promedio"], text, "0"))
            m_av     = _header["avance"].search(text)
            a_obl, a_opt, a_tot = (int(m_av.group(i)) for i in (1,2,3)) if m_av else (0,0,0)

            uac: List[UACItemDTO] = []
            for m in _row.finditer(text):
                tipo, clave, semestre, nombre, calif, horas, cred, periodo = m.groups()
                uac.append(UACItemDTO(
                    plantel="CETMAR", 
                    tipo_uac=tipo,
                    clave_uac=clave,
                    semestre=int(semestre),
                    nombre=nombre.strip(),
                    calif=None if calif == "NA" else float(calif),
                    horas_sem=int(horas),
                    creditos=None if cred == "---" else int(cred),
                    periodo=periodo.strip(),
                ))

            if not (curp or alumno or control or plan or carrera or uac):
                continue

            results.append(ReportCardDTO(
                curp=curp, alumno=alumno, numero_control=control,
                plan_estudios=plan, carrera=carrera,
                avance_oblig=a_obl, avance_opt=a_opt, avance_total=a_tot,
                promedio=promedio, uac=uac
            ))

        return results
