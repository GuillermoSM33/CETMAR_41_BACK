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
    "carrera": re.compile(r"CARRERA\s*[:\-]?\s*(.+)", re.I),
    "promedio": re.compile(r"Promedio\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)", re.I),
    "avance": re.compile(r"Avance.?Oblig.?(\d+).?Opt.?(\d+).?Total.?(\d+)", re.S | re.I),
    "semestre": re.compile(r"SEMESTRE\s*[:\-]?\s*(\d{1,2})", re.I),
    "plantel": re.compile(r"PLANTEL\s*[:\-]?\s*(.+)", re.I),
    "turno": re.compile(r"TURNO\s*[:\-]?\s*(.+)", re.I),
    "clave_ct": re.compile(r"CLAVE\s+DEL\s+CENTRO\s+DE\s+TRABAJO\s*[:\-]?\s*(.+)", re.I),
    "grupo": re.compile(r"GRUPO\s*[:\-]?\s*(.+)", re.I),
    "generacion": re.compile(r"GENERACION\s*[:\-]?\s*(.+)", re.I),
    "modalidad": re.compile(r"MODALIDAD\s*[:\-]?\s*(.+)", re.I),
    "periodo": re.compile(r"PERIODO\s*[:\-]?\s*(.+)", re.I),
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


def _normalize_text(text: str) -> str:
    head_sample = text[:800]
    if re.search(r"([A-ZÁÉÍÓÚÑ])\1", head_sample):
        return re.sub(r"([A-Za-zÁÉÍÓÚÑáéíóúñ])\1+", r"\1", text)
    return text


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


def _acreditado_from_periods(c1: Optional[Union[float, str]], c2: Optional[Union[float, str]], c3: Optional[Union[float, str]]) -> Optional[bool]:
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
            full_text = "\n".join(filter(None, ((p.extract_text() or "") for p in pdf.pages)))
            table = _extract_first_table(pdf)

        parts = [c for c in SPLIT_RX.split(full_text) if c.strip()] or ([full_text] if full_text.strip() else [])
        if not parts:
            return []

        text = parts[0]
        norm = _normalize_text(text)

        curp = _m(HEADER_RX["curp"], norm)
        alumno = _m(HEADER_RX["alumno"], norm)
        control = _m(HEADER_RX["control"], norm)
        plan = _m(HEADER_RX["plan"], norm)
        carrera = _m(HEADER_RX["carrera"], norm)
        periodo = _m(HEADER_RX["periodo"], norm)

        plantel = _m(HEADER_RX["plantel"], norm)
        turno = _m(HEADER_RX["turno"], norm)
        clave_ct = _m(HEADER_RX["clave_ct"], norm)
        grupo = _m(HEADER_RX["grupo"], norm)
        generacion = _m(HEADER_RX["generacion"], norm)
        modalidad = _m(HEADER_RX["modalidad"], norm)

        promedio = float(_m(HEADER_RX["promedio"], norm, "0") or 0)

        m_av = HEADER_RX["avance"].search(text)
        a_obl, a_opt, a_tot = (
            (int(m_av.group(1)), int(m_av.group(2)), int(m_av.group(3)))
            if m_av
            else (0, 0, 0)
        )

        semestre_default: Optional[int] = None
        sm = HEADER_RX["semestre"].search(text)
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
                periodo=periodo,
                plan_estudios=plan,
                carrera=carrera,
                turno=turno,
                grupo=grupo,
                plantel=plantel,
                clave_ct=clave_ct,
                generacion=generacion,
                modalidad=modalidad,
                semestre=semestre_default,
                avance_oblig=a_obl,
                avance_opt=a_opt,
                avance_total=a_tot,
                promedio=promedio,
                uac=uac,
            )
        ]
