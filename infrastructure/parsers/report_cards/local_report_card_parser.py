import re, pdfplumber
from typing import List, BinaryIO
from application.dtos.report_cards.report_card_dto import ReportCardDTO, UACItemDTO
from application.interfaces.report_cards.report_card_parser import IReportCardParser

# Definiciones de encabezado (Se mantienen para la extracción de metadatos)
_header = {
    "curp": re.compile(r"CURP\s*[:\-]?\s*([A-Z0-9]+)", re.I),

    "alumno": re.compile(
        r"(?:Nombre del alumno|Nombre|Alumno|NOMBRE)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ0-9\s'.-]+)",
        re.I,
    ),

    "control": re.compile(
        r"(?:N(?:úmero|º|o)\.?\s*control|No\.?\s*CONTROL|NO\.?\s*CONTROL)"
        r"\s*[:\-]?\s*([0-9A-Z-]+)",
        re.I,
    ),

    "plan": re.compile(r"\bPlan(?:\s+de\s+estudios)?\b\s*[:\-]?\s*(.+)", re.I),
    "carrera": re.compile(r"CARRERA\s*[:\-]?\s*(.+)", re.I),
    "promedio": re.compile(r"Promedio\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)", re.I),
    "avance": re.compile(
        r"Avance.?Oblig.?(\d+).?Opt.?(\d+).?Total.?(\d+)",
        re.S | re.I,
    ),
    "semestre": re.compile(r"SEMESTRE\s*[:\-]?\s*(\d{1,2})", re.I),
    
    # Campos extra del encabezado
    "plantel": re.compile(r"PLANTEL\s*[:\-]?\s*(.+)", re.I),
    "turno": re.compile(r"TURNO\s*[:\-]?\s*(.+)", re.I),
    "clave_ct": re.compile(r"CLAVE\s+DEL\s+CENTRO\s+DE\s+TRABAJO\s*[:\-]?\s*(.+)", re.I),
    "grupo": re.compile(r"GRUPO\s*[:\-]?\s*(.+)", re.I),
    "generacion": re.compile(r"GENERACION\s*[:\-]?\s*(.+)", re.I),
    "modalidad": re.compile(r"MODALIDAD\s*[:\-]?\s*(.+)", re.I),
}

# 🛑 NOTA: Se ha eliminado la función _split_table_lines y la regex _row.

class LocalReportCardParser(IReportCardParser):
    def parse_many(self, fp: BinaryIO) -> List[ReportCardDTO]:
        try:
            fp.seek(0)
        except Exception:
            pass

        with pdfplumber.open(fp) as pdf:
            # 1. Extracción de texto completo para buscar campos de encabezado
            full = "\n".join(
                filter(None, ((p.extract_text() or "") for p in pdf.pages))
            )

            # 2. Extracción de la tabla de materias usando geometría (solo la primera página)
            page = pdf.pages[0]
            tables = page.extract_tables()

        split_rx = re.compile(r"(?=HISTORIAL\s+ACAD(?:É|E)MICO)", re.I)
        parts = [c for c in split_rx.split(full) if c.strip()]
        if not parts and full.strip():
            parts = [full]

        def _m(rx: re.Pattern, text: str, default: str = "") -> str:
            m = rx.search(text)
            return m.group(1).strip() if m else default

        results: List[ReportCardDTO] = []

        # Procesamos solo la primera parte (asumiendo una boleta por PDF)
        if not parts:
            return results

        text = parts[0]
        
        # --- Extracción de encabezados ---
        head_sample = text[:800]
        duplicated_letters = bool(re.search(r"([A-ZÁÉÍÓÚÑ])\1", head_sample))
        if duplicated_letters:
            norm_text = re.sub(r"([A-Za-zÁÉÍÓÚÑáéíóúñ])\1+", r"\1", text)
        else:
            norm_text = text

        curp = _m(_header["curp"], norm_text)
        alumno = _m(_header["alumno"], norm_text)
        control = _m(_header["control"], norm_text)
        plan = _m(_header["plan"], norm_text)
        carrera = _m(_header["carrera"], norm_text)
        plantel = _m(_header.get("plantel"), norm_text)
        turno = _m(_header.get("turno"), norm_text)
        clave_ct = _m(_header.get("clave_ct"), norm_text)
        grupo = _m(_header.get("grupo"), norm_text)
        generacion = _m(_header.get("generacion"), norm_text)
        modalidad = _m(_header.get("modalidad"), norm_text)
        promedio = float(_m(_header["promedio"], norm_text, "0"))
        
        m_av = _header["avance"].search(text)
        a_obl, a_opt, a_tot = (
            (int(m_av.group(1)), int(m_av.group(2)), int(m_av.group(3)))
            if m_av
            else (0, 0, 0)
        )

        # Inicialización y extracción de semestre (Corrige error de "not defined")
        semestre_default = None
        sm = _header["semestre"].search(text)
        if sm:
            try:
                semestre_default = int(sm.group(1))
            except Exception:
                semestre_default = None
        
        # --- Lógica de Extracción de Tabla de Materias (usando extract_tables) ---
        uac: List[UACItemDTO] = []
        
        # ⚠️ Verificación: Solo procesamos si se detectó una tabla
        if tables and tables[0]:
            raw_table = tables[0]
            # Saltamos la fila de encabezados
            data_rows = raw_table[1:]

            for row in data_rows:
                # [CLAVE (0), NOMBRE (1), CALIF1 (2), CALIF2 (3), CALIF3 (4), ASIS1 (5), ASIS2 (6), ASIS3 (7)]
                
                # Verificación de longitud y datos mínimos
                if len(row) < 8 or row[0] is None or row[1] is None:
                    continue
                
                # Asignación de celdas
                clave = str(row[0]).strip()
                nombre = str(row[1]).replace('\n', ' ').strip()
                cal1_raw, cal2_raw, cal3_raw = row[2], row[3], row[4]
                asis1_raw, asis2_raw, asis3_raw = row[5], row[6], row[7]
                
                # 🆕 CORRECCIÓN AGRESIVA 1: Limpieza final del nombre de la materia
                # Eliminamos cualquier número o texto de firma que se haya filtrado en la celda [1]
                
                # 1. Busca secuencias de tokens de datos (Números, AC/NA) pegadas al final del nombre.
                # 2. Busca texto de firma (Director) que pudo haberse fusionado.
                DATA_OR_FOOTER_PATTERN = r"(\s+[\d\.]+|\s+AC|\s+NA){1,}\s*(VIRGINIA PÉREZ HERRERA.|DIRECTOR DEL PLANTEL.|1 de 1)?$"
                
                nombre = re.sub(DATA_OR_FOOTER_PATTERN, "", nombre, flags=re.I).strip()
                nombre = re.sub(r'\s{2,}', ' ', nombre).strip() # Colapsar espacios extra
                
                # --- Funciones de Conversión ---
                def to_float_or_str(val):
                    # 💡 Si la celda está vacía o es None, devolvemos None
                    if val is None or not str(val).strip(): return None
                    val = str(val).strip()
                    try:
                        return float(val)
                    except ValueError:
                        # Devuelve la cadena (ej. 'AC', 'NA')
                        return val

                def to_int_or_none(val):
                    if val is None or not str(val).strip().isdigit(): return None
                    return int(val)
                
                # Aplicación de Conversión
                cal1 = to_float_or_str(cal1_raw)
                cal2 = to_float_or_str(cal2_raw)
                cal3 = to_float_or_str(cal3_raw)
                
                asis1 = to_int_or_none(asis1_raw)
                asis2 = to_int_or_none(asis2_raw)
                asis3 = to_int_or_none(asis3_raw)

                # Lógica de acreditado
                acreditado = None
                if any(x in ("AC","NA") for x in [cal1, cal2, cal3] if isinstance(x, str)):
                    if any(v == "AC" for v in [cal1, cal2, cal3] if isinstance(v, str)):
                        acreditado = True
                    elif any(v == "NA" for v in [cal1, cal2, cal3] if isinstance(v, str)):
                        acreditado = False
                
                # Asignación de semestre
                semestre_val = semestre_default if semestre_default is not None else 0

                uac.append(
                    UACItemDTO(
                        plantel="CETMAR",
                        clave_uac=clave,
                        semestre=int(semestre_val),
                        nombre=nombre,
                        calif1=cal1, calif2=cal2, calif3=cal3,
                        asis1=asis1, asis2=asis2, asis3=asis3,
                        acreditado=acreditado,
                    )
                )

        if not (curp or alumno or control or plan or carrera or uac):
            return results

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