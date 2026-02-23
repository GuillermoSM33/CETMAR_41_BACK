import re
from typing import BinaryIO, List, Optional, Union

import pdfplumber

from application.dtos.report_cards.report_card_dto import ReportCardDTO, UACItemDTO
from application.interfaces.report_cards.report_card_parser import IReportCardParser

HEADER_RX = {
    "curp": re.compile(r"CURP\s*[:\-]?\s*([A-Z0-9]+)", re.I),
    "alumno": re.compile(
        r"(?:Nombre del alumno|Nombre|Alumno|NOMBRE)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ0-9\s'.-]+)",
        re.I,
    ),
    "control": re.compile(
        r"(?:N(?:úmero|º|o)\.?\s*control|No\.?\s*CONTROL|NO\.?\s*CONTROL)\s*[:\-]?\s*([0-9A-Z-]+)",
        re.I,
    ),
    "plan": re.compile(r"\bPlan(?:\s+de\s+estudios)?\b\s*[:\-]?\s*(.+)", re.I),
    "carrera": re.compile(r"\bCARRERA\b\s*[:\-]?\s*(.+)", re.I),
    "promedio": re.compile(r"Promedio\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)", re.I),
    "avance": re.compile(r"Avance.?Oblig.?(\d+).?Opt.?(\d+).?Total.?(\d+)", re.S | re.I),
    "semestre": re.compile(r"SEMESTRE\s*[:\-]?\s*(\d{1,2})", re.I),
    "plantel": re.compile(r"\bPLANTEL\b\s*[:\-]?\s*(.+)", re.I),
    "turno": re.compile(r"\bTURNO\b\s*[:\-]?\s*(.+)", re.I),
    "clave_ct": re.compile(r"CLAVE\s+DEL\s+CENTRO\s+DE\s+TRABAJO\s*[:\-]?\s*(.+)", re.I),
    "grupo": re.compile(r"\bGRUPO\b\s*[:\-]?\s*(.+)", re.I),
    "generacion": re.compile(r"\bGENERACI(?:O|Ó)N\b\s*[:\-]?\s*(.+)", re.I),
    "modalidad": re.compile(r"\bMODALIDAD\b\s*[:\-]?\s*(.+)", re.I),
    "periodo": re.compile(r"\bPERIODO\b\s*[:\-]?\s*(.+)", re.I),
}

SPLIT_RX = re.compile(r"(?=HISTORIAL\s+ACAD(?:É|E)MICO)", re.I)

NAME_TRAIL_RX = re.compile(
    r"(\s+[\d\.]+|\s+AC|\s+NA){1,}\s*(VIRGINIA PÉREZ HERRERA\.|DIRECTOR DEL PLANTEL\.|1 de 1)?$",
    re.I,
)

def _seek0(fp: BinaryIO) -> None:
    try:
        fp.seek(0)
    except Exception:
        return

_DOUBLED_WORD_RX = re.compile(r"\b(?:([A-Za-zÁÉÍÓÚÑáéíóúñ])\1){3,}\b", re.UNICODE)


def _dedupe_doubled_word(m: re.Match) -> str:
    w = m.group(0)
    return w[::2]

def _normalize_text(text: str) -> str:
    if not text:
        return text
    return _DOUBLED_WORD_RX.sub(_dedupe_doubled_word, text)

def _m(rx: re.Pattern, text: str, default: str = "") -> str:
    m = rx.search(text)
    return m.group(1).strip() if m else default

def _to_float_or_str(val: object) -> Optional[Union[float, str]]:
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return s

def _to_int_or_none(val: object) -> Optional[int]:
    if val is None:
        return None
    s = str(val).strip()
    if not s.isdigit():
        return None
    return int(s)

def _clean_header_value(s: str) -> str:
    return (s or "").strip().lstrip(":").strip()

STOP_LABELS = [
    "SUBSISTEMA",
    "PLANTEL",
    "CLAVE DEL CENTRO DE TRABAJO",
    "CLAVE DEL CENTRO  DE TRABAJO",
    "NO. CONTROL",
    "NO CONTROL",
    "NÚMERO CONTROL",
    "NUMERO CONTROL",
    "NOMBRE",
    "SEMESTRE",
    "CARRERA",
    "TURNO",
    "GRUPO",
    "GENERACION",
    "GENERACIÓN",
    "MODALIDAD",
    "PERIODO",
    "CURP",
]

_STOP_PAT = r"(?:\b" + "|".join(map(re.escape, STOP_LABELS)) + r"\b)\s*:"

def _extract_label_value(text: str, label_variants: list[str]) -> str:

    if not text:
        return ""

    lab_pat = r"(?:\b" + "|".join(map(re.escape, label_variants)) + r"\b)"
    rx = re.compile(rf"{lab_pat}\s*:\s*(.*?)\s*(?={_STOP_PAT}|$)", re.I | re.S)

    m = rx.search(text)
    return _clean_header_value(m.group(1)) if m else ""

def _acreditado_from_periods(
    c1: Optional[Union[float, str]],
    c2: Optional[Union[float, str]],
    c3: Optional[Union[float, str]],
) -> Optional[bool]:
    strs = [v.upper() for v in (c1, c2, c3) if isinstance(v, str)]
    if "AC" in strs:
        return True
    if "NA" in strs:
        return False
    return None

def _clean_subject_name(nombre: str) -> str:
    nombre = nombre.replace("\n", " ").strip()
    nombre = NAME_TRAIL_RX.sub("", nombre).strip()
    nombre = re.sub(r"\s{2,}", " ", nombre).strip()
    return nombre

def _extract_first_table(pdf) -> List[List[Optional[str]]]:
    page = pdf.pages[0]
    tables = page.extract_tables()
    if not tables or not tables[0]:
        return []
    return tables[0]
class LocalReportCardParser(IReportCardParser):
    def parse_many(self, fp: BinaryIO) -> List[ReportCardDTO]:
        _seek0(fp)

        with pdfplumber.open(fp) as pdf:
            full_text = "\n".join(
                filter(None, ((p.extract_text() or "") for p in pdf.pages))
            )
            table = _extract_first_table(pdf)

        parts = [c for c in SPLIT_RX.split(full_text) if c.strip()] or (
            [full_text] if full_text.strip() else []
        )
        if not parts:
            return []

        text = parts[0]

        norm = _normalize_text(text)

        curp = _clean_header_value(_m(HEADER_RX["curp"], norm))

        alumno = _clean_header_value(
            _extract_label_value(norm, ["NOMBRE", "Nombre", "Nombre del alumno", "Alumno"])
        )

        control_raw = _extract_label_value(
            norm,
            ["NO. CONTROL", "NO CONTROL", "NÚMERO CONTROL", "NUMERO CONTROL", "No. Control", "No Control"],
        )
        m_ctl = re.search(r"\b\d{8,}\b", control_raw or "")
        control = m_ctl.group(0) if m_ctl else ""

        carrera = _clean_header_value(_extract_label_value(norm, ["CARRERA", "Carrera"]))
        periodo = _clean_header_value(_extract_label_value(norm, ["PERIODO", "Periodo"]))

        plantel = _clean_header_value(_extract_label_value(norm, ["PLANTEL", "Plantel"]))
        turno = _clean_header_value(_extract_label_value(norm, ["TURNO", "Turno"]))
        clave_ct = _clean_header_value(
            _extract_label_value(norm, ["CLAVE DEL CENTRO DE TRABAJO", "CLAVE DEL CENTRO  DE TRABAJO"])
        )
        grupo = _clean_header_value(_extract_label_value(norm, ["GRUPO", "Grupo"]))

        generacion = _clean_header_value(
            _extract_label_value(norm, ["GENERACION", "GENERACIÓN", "Generacion", "Generación"])
        )
        modalidad = _clean_header_value(_extract_label_value(norm, ["MODALIDAD", "Modalidad"]))

        plan_from_rx = _clean_header_value(_m(HEADER_RX["plan"], norm))
        plan = plan_from_rx or generacion

        promedio = float(_m(HEADER_RX["promedio"], norm, "0") or 0)

        m_av = HEADER_RX["avance"].search(norm)
        a_obl, a_opt, a_tot = (
            (int(m_av.group(1)), int(m_av.group(2)), int(m_av.group(3)))
            if m_av
            else (0, 0, 0)
        )

        semestre_default: Optional[int] = None
        sm = HEADER_RX["semestre"].search(norm)
        if sm:
            try:
                semestre_default = int(sm.group(1))
            except Exception:
                semestre_default = None

        uac: List[UACItemDTO] = []
        if table:
            data_rows = table[1:]
            for row in data_rows:
                if len(row) < 8 or row[0] is None or row[1] is None:
                    continue

                clave = str(row[0]).strip()
                nombre = _clean_subject_name(str(row[1]))

                cal1 = _to_float_or_str(row[2])
                cal2 = _to_float_or_str(row[3])
                cal3 = _to_float_or_str(row[4])

                asis1 = _to_int_or_none(row[5])
                asis2 = _to_int_or_none(row[6])
                asis3 = _to_int_or_none(row[7])

                acreditado = _acreditado_from_periods(cal1, cal2, cal3)
                semestre_val = int(semestre_default or 0)

                uac.append(
                    UACItemDTO(
                        plantel=plantel or "CETMAR",
                        clave_uac=clave,
                        semestre=semestre_val,
                        nombre=nombre,
                        calif1=cal1,
                        calif2=cal2,
                        calif3=cal3,
                        asis1=asis1,
                        asis2=asis2,
                        asis3=asis3,
                        acreditado=acreditado,
                    )
                )

        if not (curp or alumno or control or plan or carrera or uac):
            return []

        return [
            ReportCardDTO(
                curp=curp,
                alumno=alumno,
                numero_control=control,
                periodo=periodo or "SIN_PERIODO",
                plan_estudios=plan or "SIN_PLAN",
                carrera=carrera or "SIN_CARRERA",
                turno=turno or "",
                grupo=grupo or "",
                plantel=plantel or "",
                clave_ct=clave_ct or "",
                generacion=generacion or None,
                modalidad=modalidad or None,
                semestre=semestre_default,
                avance_oblig=a_obl,
                avance_opt=a_opt,
                avance_total=a_tot,
                promedio=promedio,
                uac=uac,
            )
        ]