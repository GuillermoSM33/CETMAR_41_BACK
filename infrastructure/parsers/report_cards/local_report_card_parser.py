# infrastructure/parsers/report_cards/local_report_card_parser.py
import re, pdfplumber
from typing import List, BinaryIO
from application.dtos.report_cards.report_card_dto import ReportCardDTO, UACItemDTO
from application.interfaces.report_cards.report_card_parser import IReportCardParser

_header = {
    "curp": re.compile(r"CURP\s*[:\-]?\s*([A-Z0-9]+)", re.I),

    "alumno": re.compile(
        r"(?:Nombre del alumno|Nombre|Alumno|NOMBRE)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ0-9\s'.-]+)",
        re.I,
    ),

    "control": re.compile(
        r"(?:N(?:úmero|º|o)\.?\s*control|No\.?\s*CONTROL|NO\. CONTROL|NO CONTROL|NO\. CONTROL)"
        r"\s*[:\-]?\s*([0-9A-Z-]+)",
        re.I,
    ),

    # Use word-boundary so 'PLANTEL' is not matched as 'Plan'
    "plan": re.compile(r"\bPlan(?:\s+de\s+estudios)?\b\s*[:\-]?\s*(.+)", re.I),

    # Extra header fields to capture and avoid bleeding into other fields
    "plantel": re.compile(r"PLANTEL\s*[:\-]?\s*(.+)", re.I),
    "turno": re.compile(r"TURNO\s*[:\-]?\s*(.+)", re.I),
    "clave_ct": re.compile(r"CLAVE\s+DEL\s+CENTRO\s+DE\s+TRABAJO\s*[:\-]?\s*(.+)", re.I),
    "grupo": re.compile(r"GRUPO\s*[:\-]?\s*(.+)", re.I),
    "generacion": re.compile(r"GENERACION\s*[:\-]?\s*(.+)", re.I),
    "modalidad": re.compile(r"MODALIDAD\s*[:\-]?\s*(.+)", re.I),

    "carrera": re.compile(r"CARRERA\s*[:\-]?\s*(.+)", re.I),

    "promedio": re.compile(r"Promedio\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)", re.I),

    "avance": re.compile(
        r"Avance.*?Oblig.*?(\d+).*?Opt.*?(\d+).*?Total.*?(\d+)",
        re.S | re.I,
    ),

    "semestre": re.compile(r"SEMESTRE\s*[:\-]?\s*(\d{1,2})", re.I),
}

_row = re.compile(r"^\s*([0-9]{2,6}[0-9A-Z\-]{0,20})\s+(.+)$")


def _split_table_lines(text: str) -> List[str]:
    """
    Obtiene únicamente las líneas que parecen filas de tabla de UACs,
    es decir, las que comienzan con una clave como 30310-0002-23CA, etc.
    """
    lines = [l.rstrip() for l in text.splitlines()]
    table_lines = []

    for ln in lines:
        if _row.match(ln):
            table_lines.append(ln)

    return table_lines


class LocalReportCardParser(IReportCardParser):
    def parse_many(self, fp: BinaryIO) -> List[ReportCardDTO]:
        try:
            fp.seek(0)
        except Exception:
            pass

        with pdfplumber.open(fp) as pdf:
            full = "\n".join(
                filter(None, ((p.extract_text() or "") for p in pdf.pages))
            )

        split_rx = re.compile(r"(?=HISTORIAL\s+ACAD(?:É|E)MICO)", re.I)
        parts = [c for c in split_rx.split(full) if c.strip()]

        if not parts and full.strip():
            parts = [full]

        def _m(rx: re.Pattern, text: str, default: str = "") -> str:
            m = rx.search(text)
            return m.group(1).strip() if m else default

        results: List[ReportCardDTO] = []

        for text in parts:
            # Detectar posible artefacto de texto con letras duplicadas (NNOOMMBBRREE)
            head_sample = text[:800]
            duplicated_letters = bool(re.search(r"([A-ZÁÉÍÓÚÑ])\1", head_sample))
            if duplicated_letters:
                # Normalizar duplicados: AA -> A, sólo para letras (preserva números/otros)
                norm_text = re.sub(r"([A-Za-zÁÉÍÓÚÑáéíóúñ])\1+", r"\1", text)
            else:
                norm_text = text

            if not (
                _header["curp"].search(norm_text)
                or _header["alumno"].search(norm_text)
                or _header["control"].search(norm_text)
                or _row.search(text)
            ):
                continue

            # Use normalized text for header extraction, original text for table rows
            curp = _m(_header["curp"], norm_text)
            alumno = _m(_header["alumno"], norm_text)
            control = _m(_header["control"], norm_text)
            plan = _m(_header["plan"], norm_text)
            carrera = _m(_header["carrera"], norm_text)

            # capture extra header fields
            plantel = _m(_header.get("plantel"), norm_text)
            turno = _m(_header.get("turno"), norm_text)
            clave_ct = _m(_header.get("clave_ct"), norm_text)
            grupo = _m(_header.get("grupo"), norm_text)
            generacion = _m(_header.get("generacion"), norm_text)
            modalidad = _m(_header.get("modalidad"), norm_text)
            promedio = float(_m(_header["promedio"], norm_text, "0"))

            # Fallback por línea para nombres que no se capturaron con la búsqueda global
            if not alumno:
                m_line = re.search(r"^\s*(?:Nombre del alumno|Nombre|Alumno|NOMBRE)\s*[:\-]?\s*(.+)$", norm_text, re.I | re.M)
                if m_line:
                    alumno = m_line.group(1).strip()

            # Clean alumno field from trailing labels that sometimes follow on same line
            if alumno:
                # remove leading stray colons or extra text like 'MODALIDAD: BT' appended
                alumno = re.sub(r"^[:\s-]+", "", alumno)
                alumno = re.sub(r"\s*(?:MODALIDAD|GRUPO|TURNO|PLANTEL|CLAVE\s+DEL\s+CENTRO\s+DE\s+TRABAJO|GENERACION)\s*[:\-].*$", "", alumno, flags=re.I).strip()

            # Limpieza y normalización del campo 'alumno'
            if alumno:
                # eliminar prefijos de dos puntos o guiones sobrantes
                alumno = re.sub(r'^[\s\:\-\–]+', '', alumno).strip()
                # si incluye etiquetas restantes como 'MODALIDAD' o 'PLANTEL', cortar ahí
                alumno = re.split(r'\bMODALIDAD\b[:\s\-]*', alumno, flags=re.I)[0].strip()
                alumno = re.split(r'\bPLANTEL\b[:\s\-]*', alumno, flags=re.I)[0].strip()
                # colapsar espacios múltiples y limpiar espacios sobrantes
                alumno = re.sub(r'\s{2,}', ' ', alumno).strip()

            m_av = _header["avance"].search(text)
            a_obl, a_opt, a_tot = (
                (int(m_av.group(1)), int(m_av.group(2)), int(m_av.group(3)))
                if m_av
                else (0, 0, 0)
            )

            semestre_default = None
            sm = _header["semestre"].search(text)
            if sm:
                try:
                    semestre_default = int(sm.group(1))
                except Exception:
                    semestre_default = None

            uac: List[UACItemDTO] = []
            table_lines = _split_table_lines(text)

            for ln in table_lines:
                m = _row.match(ln)
                if not m:
                    continue

                clave = m.group(1).strip()
                rest = m.group(2).strip()

                split_name = re.split(r"\s+(?=\d)", rest)
                nombre = split_name[0].strip()

                nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", rest)]
                calif = nums[-1] if nums else None  

                suf = re.search(r"-([A-Za-z0-9]+)$", clave)
                tipo_uac_val = suf.group(1) if suf else ""

                semestre_val = semestre_default if semestre_default is not None else 0

                uac.append(
                    UACItemDTO(
                        plantel="CETMAR",
                        tipo_uac=tipo_uac_val,
                        clave_uac=clave,
                        semestre=int(semestre_val),
                        nombre=nombre,
                        calif=calif,
                        horas_sem=0,
                        creditos=None,
                        periodo="",
                    )
                )

            if not (curp or alumno or control or plan or carrera or uac):
                continue

            results.append(
                ReportCardDTO(
                    curp=curp,
                    alumno=alumno,
                    numero_control=control,
                    plan_estudios=plan,
                    carrera=carrera,
                    avance_oblig=a_obl,
                    avance_opt=a_opt,
                    avance_total=a_tot,
                    promedio=promedio,
                    uac=uac,
                )
            )

        return results
