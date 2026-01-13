from typing import List, Any
from sqlalchemy.orm import Session
from infrastructure.persistence.models.identity_model import IdentityModel
from infrastructure.persistence.models.report_card_model import ReportCardModel
from infrastructure.persistence.models.report_card_item_model import ReportCardItemModel
from infrastructure.persistence.models.uac_model import UACModel
from application.dtos.report_cards.report_card_response_dto import StoredReportCardDTO, StoredUACItemDTO
from sqlalchemy.orm import joinedload


def save_parsed_report_cards(db: Session, parsed_results: List[Any], sha256: str) -> List[StoredReportCardDTO]:

    saved_rcs: List[ReportCardModel] = []

    for dto in parsed_results:
        identity = None
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

        existing_rc = db.query(ReportCardModel).filter(ReportCardModel.Src_SHA256 == sha256, ReportCardModel.Identity_ID == identity.Id).first()
        if existing_rc:
            saved_rcs.append(existing_rc)
            continue

        rc = ReportCardModel(
            Identity_ID=identity.Id,
            Periodo=dto.uac[0].periodo if dto.uac and len(dto.uac) > 0 else "",
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

            rci = ReportCardItemModel(
                ReportCard_ID=rc.Id,
                UAC_ID=uac.Id if uac else None,
                Clave_UAC=item.clave_uac,
                Semestre=item.semestre,
                Nombre=item.nombre,
                Tipo_UAC=item.tipo_uac,
                Calificacion=item.calif,
                Horas_Sem=item.horas_sem,
                Creditos=item.creditos,
                Periodo_Item=item.periodo,
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


def get_stored_report_card(db: Session, report_card_id: int) -> StoredReportCardDTO:
    rc = db.query(ReportCardModel).options(joinedload(ReportCardModel.items), joinedload(ReportCardModel.identity)).filter(ReportCardModel.Id == report_card_id).first()
    if not rc:
        raise KeyError("not found")

    items = []
    for it in rc.items:
        items.append(StoredUACItemDTO(
            clave_uac=it.Clave_UAC,
            semestre=it.Semestre,
            nombre=it.Nombre,
            tipo_uac=it.Tipo_UAC,
            calif=float(it.Calificacion) if it.Calificacion is not None else None,
            horas_sem=it.Horas_Sem,
            creditos=it.Creditos,
            periodo=it.Periodo_Item,
        ))

    dto = StoredReportCardDTO(
        id=rc.Id,
        identity_id=rc.Identity_ID,
        curp=rc.identity.CURP if rc.identity else None,
        alumno=rc.identity.Full_Name if rc.identity else None,
        numero_control=rc.identity.Student_Control_Number if rc.identity else None,
        periodo=rc.Periodo,
        plan_estudios=rc.Plan_Estudios,
        carrera=rc.Carrera,
        avance_oblig=rc.Avance_Oblig,
        avance_opt=rc.Avance_Opt,
        avance_total=rc.Avance_Total,
        promedio=float(rc.Promedio) if rc.Promedio is not None else 0.0,
        src_sha256=rc.Src_SHA256,
        created_at=rc.Created_At,
        updated_at=rc.Updated_At,
        items=items,
    )

    return dto
