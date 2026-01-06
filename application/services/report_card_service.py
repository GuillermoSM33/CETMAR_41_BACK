from typing import List, Any
from sqlalchemy.orm import Session
from infrastructure.persistence.models.identity_model import IdentityModel
from infrastructure.persistence.models.report_card_model import ReportCardModel
from infrastructure.persistence.models.report_card_item_model import ReportCardItemModel
from infrastructure.persistence.models.uac_model import UACModel
from application.dtos.report_cards.report_card_response_dto import StoredReportCardDTO, StoredUACItemDTO
from sqlalchemy.orm import joinedload
import fitz
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..")

def save_parsed_report_cards(db: Session, parsed_results: List[Any], sha256: str, pdf_content: bytes) -> List[StoredReportCardDTO]:

    saved_rcs: List[ReportCardModel] = []

    storage_path = os.path.normpath(os.path.join(project_root, "app", "storage"))
    if not os.path.exists(storage_path):
        os.makedirs(storage_path, exist_ok=True)

    for dto in parsed_results:
        identity = None
        control_num = getattr(dto, "numero_control", "documento_sin_control")

        if getattr(dto, "numero_control", None):
            identity = db.query(IdentityModel).filter(IdentityModel.Student_Control_Number == dto.numero_control).first()
        if not identity and getattr(dto, "curp", None):
            identity = db.query(IdentityModel).filter(IdentityModel.CURP == dto.curp).first()

        if not identity:
            identity = IdentityModel(
                Student_Control_Number=dto.numero_control,
                CURP=dto.curp,
                Full_Name=dto.alumno,
            )
            db.add(identity)
            db.flush()

        existing_rc = db.query(ReportCardModel).filter(
            ReportCardModel.Src_SHA256 == sha256, 
            ReportCardModel.Identity_ID == identity.Id
        ).first()

        full_file_path = os.path.join(storage_path, f"{control_num}.pdf")
        file_exists = os.path.exists(full_file_path)

        # Si el registro existe en DB y el archivo físico está presente, saltamos el proceso pesado
        if existing_rc and file_exists:
            saved_rcs.append(existing_rc)
            continue

        # Solo se ejecuta si es un archivo nuevo, cambió el hash, o se borró el PDF de la carpeta
        try:
            pdf_signed = apply_seal(pdf_content)
        except Exception as e:
            pdf_signed = pdf_content

        # Almacenamiento Local (Sobrescribe si el archivo existía pero el Hash era distinto)
        with open(full_file_path, "wb") as f:
            f.write(pdf_signed)
            f.flush()
            os.fsync(f.fileno())

        if existing_rc:
            saved_rcs.append(existing_rc)
            continue

        rc = ReportCardModel(
            Identity_ID=identity.Id,
            Periodo="",
            Plan_Estudios=dto.plan_estudios,
            Carrera=dto.carrera,
            Avance_Oblig=dto.avance_oblig,
            Avance_Opt=dto.avance_opt,
            Avance_Total=dto.avance_total,
            Promedio=dto.promedio,
            Src_SHA256=sha256,
        )
        db.add(rc)
        db.flush()

        seen_keys = set()
        for item in dto.uac:
            # DEBUG: inspect incoming parsed item before persisting
            try:
                _item_dump = item.model_dump()
            except Exception:
                try:
                    _item_dump = item.__dict__
                except Exception:
                    _item_dump = str(item)
            print("[DEBUG] Saving item for clave=", getattr(item, 'clave_uac', None), "->", _item_dump)

            key = (item.clave_uac, item.semestre)
            if key in seen_keys:
                continue

            dup = db.query(ReportCardItemModel).filter(
                ReportCardItemModel.ReportCard_ID == rc.Id,
                ReportCardItemModel.Clave_UAC == item.clave_uac,
                ReportCardItemModel.Semestre == item.semestre,
            ).first()
            if dup:
                seen_keys.add(key)
                continue

            uac = None
            if getattr(item, "clave_uac", None):
                uac = db.query(UACModel).filter(UACModel.Clave == item.clave_uac).first()

            # Convert and persist per-period fields. Calificaciones stored as strings
            # (to support 'AC'/'NA') and asistencias as integers.
            rci = ReportCardItemModel(
                ReportCard_ID=rc.Id,
                UAC_ID=uac.Id if uac else None,
                Clave_UAC=item.clave_uac,
                Semestre=item.semestre,
                Nombre=item.nombre,
                Calificacion1=str(item.calif1) if getattr(item, 'calif1', None) is not None else None,
                Calificacion2=str(item.calif2) if getattr(item, 'calif2', None) is not None else None,
                Calificacion3=str(item.calif3) if getattr(item, 'calif3', None) is not None else None,
                Asistencia1=int(item.asis1) if getattr(item, 'asis1', None) is not None and str(item.asis1).isdigit() else None,
                Asistencia2=int(item.asis2) if getattr(item, 'asis2', None) is not None and str(item.asis2).isdigit() else None,
                Asistencia3=int(item.asis3) if getattr(item, 'asis3', None) is not None and str(item.asis3).isdigit() else None,
                Calificacion=(float(item.calif3) if isinstance(item.calif3, (int,float)) else (float(item.calif2) if isinstance(item.calif2, (int,float)) else (float(item.calif1) if isinstance(item.calif1, (int,float)) else None))),
            )
            db.add(rci)
            seen_keys.add(key)

        db.commit()
        saved_rcs.append(rc)

    # map saved models to DTOs to return summary with IDs
    saved_dtos: List[StoredReportCardDTO] = []
    for rc in saved_rcs:
        saved_dtos.append(get_stored_report_card(db, rc.Id))

    return saved_dtos

def apply_seal(pdf_bytes: bytes) -> bytes:
    """Inserta firma y sello en el PDF y retorna los bytes."""
    PATH_FIRMA = os.path.normpath(os.path.join(project_root, "app", "File", "signature.png"))
    PATH_SELLO = os.path.normpath(os.path.join(project_root, "app", "File", "seal.png"))

    if not os.path.exists(PATH_FIRMA) or not os.path.exists(PATH_SELLO):
        raise FileNotFoundError("Recursos de imagen no encontrados.")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    # Se asume que la boleta es de una página
    page = doc[0] 
    w, h = page.rect.width, page.rect.height

    f_w = 180
    c_x = (w / 2) - (f_w / 2)
    
    rect_f = fitz.Rect(c_x, h - 155, c_x + f_w, h - 75)
    rect_s = fitz.Rect(w - 190, h - 145, w - 60, h - 25)

    page.insert_image(rect_f, filename=PATH_FIRMA, keep_proportion=True)
    page.insert_image(rect_s, filename=PATH_SELLO, keep_proportion=True)

    out = doc.tobytes()
    doc.close()
    return out

def get_stored_report_card(db: Session, report_card_id: int) -> StoredReportCardDTO:
    rc = db.query(ReportCardModel).options(joinedload(ReportCardModel.items), joinedload(ReportCardModel.identity)).filter(ReportCardModel.Id == report_card_id).first()
    if not rc:
        raise KeyError("not found")

    items = []
    for it in rc.items:
        # Convert stored string califications back to number when possible
        def _parse_cal(s):
            if s is None:
                return None
            try:
                return float(s)
            except Exception:
                return str(s)

        items.append(StoredUACItemDTO(
            clave_uac=it.Clave_UAC,
            semestre=it.Semestre,
            nombre=it.Nombre,
            calif1=_parse_cal(it.Calificacion1),
            calif2=_parse_cal(it.Calificacion2),
            calif3=_parse_cal(it.Calificacion3),
            asis1=it.Asistencia1,
            asis2=it.Asistencia2,
            asis3=it.Asistencia3,
            acreditado=None,
        ))

    dto = StoredReportCardDTO(
        id=rc.Id,
        identity_id=rc.Identity_ID,
        curp=rc.identity.CURP if rc.identity else None,
        alumno=rc.identity.Full_Name if rc.identity else None,
        numero_control=rc.identity.Student_Control_Number if rc.identity else None,
        src_sha256=rc.Src_SHA256,
        created_at=rc.Created_At,
        updated_at=rc.Updated_At,
        items=items,
    )

    return dto

def get_report(control_number: str) -> str:
    """Descargar boleta del estudiante"""
    storage_path = os.path.normpath(os.path.join(project_root, "app", "storage"))
    file_path = os.path.join(storage_path, f"{control_number}.pdf")
    
    # Validamos si el archivo físico existe
    if not os.path.exists(file_path):
        return None
        
    return file_path