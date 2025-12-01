from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from infrastructure.persistence.models.user_model import UserModel
from infrastructure.persistence.models.role_model import RoleModel
from application.dtos.students.update_student_dto import UpdateStudentDTO
from application.dtos.students.get_student_dto import GetStudentDetailDTO
from typing import List, Any

def get_all_students_service(db: Session, role_name: str) -> List[GetStudentDetailDTO]:
    
    # 1. Buscar el Role ID
    role = db.query(RoleModel).filter(RoleModel.Role_Name == role_name).first()
    if not role:
        return []
    
    # 2. Cargar Usuarios y su Identity en una sola consulta (JOINEDLOAD)
    # Esto es vital para evitar problemas de rendimiento (consultas N+1)
    users_with_identity = db.query(UserModel).options(
        joinedload(UserModel.identity) # Carga ansiosa de la relación 'identity'
    ).filter(
        UserModel.FK_Rol_ID == role.Id
    ).all()
    
    # 3. Mapear Modelos a DTOs
    result_dtos: List[GetStudentDetailDTO] = []
    
    for user in users_with_identity:
        # La relación 'identity' se carga gracias al joinedload
        identity_data = user.identity
        
        # Mapeo Manual: Pasamos los campos de UserModel y los de IdentityModel
        dto = GetStudentDetailDTO(
            # Campos de UserModel (Base DTO, incluyendo las FKs obligatorias)
            Id=user.Id,
            User_Name=user.User_Name,
            User_Email=user.User_Email,
            Telephone=user.Telephone,
            FK_Rol_ID=user.FK_Rol_ID,
            FK_Identity_ID=user.FK_Identity_ID,
            
            # Campos de IdentityModel (Añadidos en GetStudentDetailDTO)
            # Nota: Si los nombres de los campos en IdentityModel son diferentes, ajusta aquí:
            Matricula=identity_data.Student_Identity if identity_data and hasattr(identity_data, 'Student_Identity') else None,
            Numero_Control=identity_data.Student_Control_Number if identity_data else None,
            CURP=identity_data.CURP if identity_data else None,
            
            # Grupo / Carrera
            Grupo=identity_data.Group if identity_data and hasattr(identity_data, 'Group') else None,
            Carrera=identity_data.Major if identity_data and hasattr(identity_data, 'Major') else None,
        )
        result_dtos.append(dto)

    return result_dtos
    role = db.query(RoleModel).filter(RoleModel.Role_Name == role_name).first()
    if not role:
        return []
    return db.query(UserModel).filter(UserModel.FK_Rol_ID == role.Id).all()

def update_student_service(db: Session, user_id: int, student_data: UpdateStudentDTO) -> UserModel:
    student = db.query(UserModel).filter(UserModel.Id == user_id).first()
    if not student:
        raise Exception("Usuario no encontrado")

    student.User_Name = student_data.User_Name
    student.User_Email = student_data.User_Email
    student.FK_Rol_ID = student_data.FK_Rol_ID
    student.Telephone = int(student_data.Telephone)
    student.FK_Identity_ID = student_data.FK_Identity_ID

    db.commit()
    db.refresh(student)
    return student