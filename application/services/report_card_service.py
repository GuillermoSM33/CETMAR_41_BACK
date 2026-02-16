from __future__ import annotations

import os
from typing import Any, List, Optional, Tuple, Union

import fitz
from sqlalchemy.orm import Session, joinedload

from application.dtos.report_cards.report_card_response_dto import (
    StoredReportCardDTO,
    StoredUACItemDTO,
)
from infrastructure.persistence.models.identity_model import IdentityModel
from infrastructure.persistence.models.report_card_item_model import ReportCardItemModel
from infrastructure.persistence.models.report_card_model import ReportCardModel
from infrastructure.persistence.models.uac_model import UACModel

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(CURRENT_DIR, "..", "..")
STORAGE_PATH = os.path.normpath(os.path.join(PROJECT_ROOT, "app", "storage"))
SIGNATURE_PATH = os.path.normpath(os.path.join(PROJECT_ROOT, "app", "File", "signature.png"))
SEAL_PATH = os.path.normpath(os.path.join(PROJECT_ROOT, "app", "File", "seal.png"))


def save_parsed_report_cards(
    db: Session,
    parsed_results: List[Any],
    sha256: str,
    pdf_content: bytes,
) -> List[StoredReportCardDTO]:
    os.makedirs(STORAGE_PATH, exist_ok=True)

    saved_ids: List[int] = []

    for dto in parsed_results:
        identity = _get_or_create_identity(db, dto)
        _sync_identity_from_report(dto, identity)

        control_num = getattr(dto, "numero_control", None) or "documento_sin_control"
        pdf_path = os.path.join(STORAGE_PATH, f"{control_num}.pdf")

        existing_rc = _get_existing_report_card(db, identity_id=identity.Id, sha256=sha256)
        if existing_rc and os.path.exists(pdf_path):
            saved_ids.append(existing_rc.Id)
            continue

        _write_pdf(pdf_path, _try_apply_seal(pdf_content))

        if existing_rc:
            saved_ids.append(existing_rc.Id)
            continue

        rc = _create_report_card(db, dto, identity_id=identity.Id, sha256=sha256)
        _save_report_items(db, rc_id=rc.Id, items=getattr(dto, "uac", []))
        db.commit()
        saved_ids.append(rc.Id)

    return [get_stored_report_card(db, rc_id) for rc_id in saved_ids]


def _get_or_create_identity(db: Session, dto: Any) -> IdentityModel:
    identity: Optional[IdentityModel] = None

    control = getattr(dto, "numero_control", None)
    if control:
        identity = (
            db.query(IdentityModel)
            .filter(IdentityModel.Student_Control_Number == control)
            .first()
        )

    curp = getattr(dto, "curp", None)
    if not identity and curp:
        identity = db.query(IdentityModel).filter(IdentityModel.CURP == curp).first()

    if identity:
        return identity

    identity = IdentityModel(
        Student_Control_Number=control,
        CURP=curp,
        Full_Name=getattr(dto, "alumno", None),
    )
    db.add(identity)
    db.flush()
    return identity


def _sync_identity_from_report(dto: Any, identity: IdentityModel) -> None:
    alumno = getattr(dto, "alumno", None)
    if alumno:
        identity.Full_Name = alumno

    grupo = getattr(dto, "grupo", None)
    if grupo:
        identity.Grupo = grupo

    turno = getattr(dto, "turno", None)
    if turno:
        identity.Schedule = turno

    carrera = getattr(dto, "carrera", None)
    if carrera:
        identity.Major = carrera


def _get_existing_report_card(db: Session, identity_id: int, sha256: str) -> Optional[ReportCardModel]:
    return (
        db.query(ReportCardModel)
        .filter(ReportCardModel.Src_SHA256 == sha256, ReportCardModel.Identity_ID == identity_id)
        .first()
    )


def _create_report_card(db: Session, dto: Any, identity_id: int, sha256: str) -> ReportCardModel:
    periodo = (getattr(dto, "periodo", None) or "").strip() or "SIN_PERIODO"
    rc = ReportCardModel(
        Identity_ID=identity_id,
        Periodo=periodo,
        Plan_Estudios=getattr(dto, "plan_estudios", None),
        Carrera=getattr(dto, "carrera", None),
        Avance_Oblig=int(getattr(dto, "avance_oblig", 0) or 0),
        Avance_Opt=int(getattr(dto, "avance_opt", 0) or 0),
        Avance_Total=int(getattr(dto, "avance_total", 0) or 0),
        Promedio=float(getattr(dto, "promedio", 0) or 0),
        Src_SHA256=sha256,
    )
    db.add(rc)
    db.flush()
    return rc


def _save_report_items(db: Session, rc_id: int, items: List[Any]) -> None:
    seen: set[Tuple[str, int]] = set()

    for item in items:
        clave = getattr(item, "clave_uac", None)
        semestre = getattr(item, "semestre", None)

        if not clave or semestre is None:
            continue

        key = (str(clave), int(semestre))
        if key in seen:
            continue
        seen.add(key)

        exists = (
            db.query(ReportCardItemModel)
            .filter(
                ReportCardItemModel.ReportCard_ID == rc_id,
                ReportCardItemModel.Clave_UAC == key[0],
                ReportCardItemModel.Semestre == key[1],
            )
            .first()
        )
        if exists:
            continue

        uac = (
            db.query(UACModel).filter(UACModel.Clave == key[0]).first()
            if key[0]
            else None
        )

        cal1 = getattr(item, "calif1", None)
        cal2 = getattr(item, "calif2", None)
        cal3 = getattr(item, "calif3", None)

        rci = ReportCardItemModel(
            ReportCard_ID=rc_id,
            UAC_ID=uac.Id if uac else None,
            Clave_UAC=key[0],
            Semestre=key[1],
            Nombre=getattr(item, "nombre", "") or "",
            Calificacion1=_to_str_or_none(cal1),
            Calificacion2=_to_str_or_none(cal2),
            Calificacion3=_to_str_or_none(cal3),
            Asistencia1=_to_int_or_none(getattr(item, "asis1", None)),
            Asistencia2=_to_int_or_none(getattr(item, "asis2", None)),
            Asistencia3=_to_int_or_none(getattr(item, "asis3", None)),
            Calificacion=_to_float_or_none(cal3)
            or _to_float_or_none(cal2)
            or _to_float_or_none(cal1),
        )
        db.add(rci)


def _to_str_or_none(v: Any) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _to_int_or_none(v: Any) -> Optional[int]:
    if v is None:
        return None
    s = str(v).strip()
    if not s.isdigit():
        return None
    return int(s)


def _to_float_or_none(v: Any) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        return None


def _try_apply_seal(pdf_bytes: bytes) -> bytes:
    try:
        return apply_seal(pdf_bytes)
    except Exception:
        return pdf_bytes


def _write_pdf(path: str, pdf_bytes: bytes) -> None:
    with open(path, "wb") as f:
        f.write(pdf_bytes)
        f.flush()
        os.fsync(f.fileno())


def apply_seal(pdf_bytes: bytes) -> bytes:
    if not os.path.exists(SIGNATURE_PATH) or not os.path.exists(SEAL_PATH):
        raise FileNotFoundError("Recursos de imagen no encontrados.")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[0]
    w, h = page.rect.width, page.rect.height

    firma_w = 180
    firma_x = (w / 2) - (firma_w / 2)

    rect_firma = fitz.Rect(firma_x, h - 155, firma_x + firma_w, h - 75)
    rect_sello = fitz.Rect(w - 190, h - 145, w - 60, h - 25)

    page.insert_image(rect_firma, filename=SIGNATURE_PATH, keep_proportion=True)
    page.insert_image(rect_sello, filename=SEAL_PATH, keep_proportion=True)

    out = doc.tobytes()
    doc.close()
    return out


def get_stored_report_card(db: Session, report_card_id: int) -> StoredReportCardDTO:
    rc = (
        db.query(ReportCardModel)
        .options(
            joinedload(ReportCardModel.items).joinedload(ReportCardItemModel.uac),
            joinedload(ReportCardModel.identity),
        )
        .filter(ReportCardModel.Id == report_card_id)
        .first()
    )
    if not rc:
        raise KeyError("not found")

    items: List[StoredUACItemDTO] = []
    for it in rc.items:
        cal1 = _parse_cal(it.Calificacion1)
        cal2 = _parse_cal(it.Calificacion2)
        cal3 = _parse_cal(it.Calificacion3)
        final_cal = float(it.Calificacion) if it.Calificacion is not None else None
        acreditado = _acreditado(final_cal, cal1, cal2, cal3)

        items.append(
            StoredUACItemDTO(
                clave_uac=it.Clave_UAC,
                semestre=it.Semestre,
                nombre=it.Nombre,
                tipo_uac=(it.uac.Tipo if it.uac else None),
                horas_sem=(it.uac.Horas_Sem if it.uac else None),
                creditos=(it.uac.Creditos if it.uac else None),
                periodo=rc.Periodo,
                calif=final_cal,
                calif1=cal1,
                calif2=cal2,
                calif3=cal3,
                asis1=it.Asistencia1,
                asis2=it.Asistencia2,
                asis3=it.Asistencia3,
                acreditado=acreditado,
            )
        )

    return StoredReportCardDTO(
        id=rc.Id,
        identity_id=rc.Identity_ID,
        curp=(rc.identity.CURP if rc.identity else None),
        alumno=(rc.identity.Full_Name if rc.identity else None),
        numero_control=(rc.identity.Student_Control_Number if rc.identity else None),
        periodo=rc.Periodo,
        plan_estudios=rc.Plan_Estudios,
        carrera=rc.Carrera,
        avance_oblig=int(rc.Avance_Oblig or 0),
        avance_opt=int(rc.Avance_Opt or 0),
        avance_total=int(rc.Avance_Total or 0),
        promedio=float(rc.Promedio or 0),
        src_sha256=rc.Src_SHA256,
        created_at=rc.Created_At,
        updated_at=rc.Updated_At,
        items=items,
    )


def _parse_cal(s: Optional[str]) -> Optional[Union[float, str]]:
    if s is None:
        return None
    try:
        return float(s)
    except Exception:
        return str(s)


def _acreditado(
    final_cal: Optional[float],
    cal1: Optional[Union[float, str]],
    cal2: Optional[Union[float, str]],
    cal3: Optional[Union[float, str]],
) -> Optional[bool]:
    for v in (cal1, cal2, cal3):
        if isinstance(v, str):
            code = v.strip().upper()
            if code == "AC":
                return True
            if code == "NA":
                return False
    if final_cal is None:
        return None
    return final_cal >= 6


def get_report(control_number: str) -> Optional[str]:
    file_path = os.path.join(STORAGE_PATH, f"{control_number}.pdf")
    return file_path if os.path.exists(file_path) else None
