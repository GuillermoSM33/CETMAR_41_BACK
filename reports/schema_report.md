## Informe de esquema de la base de datos

Fecha: 2025-10-24

Este documento describe las tablas definidas en `infrastructure/persistence/models`.

---

### `passwords` (AuthModel)
- Clase: `AuthModel`
- __tablename__: `passwords`
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `FK_User_ID` — Integer, ForeignKey("users.Id"), unique=True
  - `Hashed_Password` — String(255)
- Relaciones:
  - `user` — relationship("UserModel", back_populates="auth") (1:1)

---

### `roles` (RoleModel)
- Clase: `RoleModel`
- __tablename__: `roles`
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `Role_Name` — String(50)
- Relaciones:
  - `users` — relationship("UserModel", back_populates="role") (1 role tiene muchos usuarios)

---

### `tokens` (TokenModel)
- Clase: `TokenModel`
- __tablename__: `tokens`
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `Token` — String(400), unique=True
  - `InBlackList` — Boolean, default=False
  - `FK_User_ID` — Integer, ForeignKey("users.Id")
  - `Date_Expiration_Time` — Date
- Relaciones:
  - `user` — relationship("UserModel", back_populates="tokens")

---

### `users` (UserModel)
- Clase: `UserModel`
- __tablename__: `users`
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `User_Name` — String(80)
  - `User_Email` — String(100), unique=True
  - `FK_Rol_ID` — Integer, ForeignKey("roles.Id")
  - `Telephone` — BigInteger
  - `FK_Identity_ID` — Integer, ForeignKey("identities.Id")
- Relaciones:
  - `role` — relationship("RoleModel", back_populates="users")
  - `identity` — relationship("IdentityModel", back_populates="users")
  - `tokens` — relationship("TokenModel", back_populates="user")
  - `califications` — relationship("CalificationModel", back_populates="user")
  - `auth` — relationship("AuthModel", back_populates="user", uselist=False)

---

### `identities` (IdentityModel)
- Clase: `IdentityModel`
- __tablename__: `identities`
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `Student_Control_Number` — String(32), unique=True, nullable=False
  - `CURP` — String(20), nullable=True, unique=True
  - `Full_Name` — String(200), nullable=True
  - `Student_Identity` — Integer, nullable=True
  - `Teacher_Identity` — Integer, nullable=True
  - `Management_Admin_Identity` — Integer, nullable=True
  - `Schedule` — String(80), nullable=True
  - `Major` — String(150), nullable=True
- Relaciones:
  - `users` — relationship("UserModel", back_populates="identity")
  - `report_cards` — relationship("ReportCardModel", back_populates="identity")
  - `raw_report_cards` — relationship("ReportCardRawModel", back_populates="identity")

---

### `califications` (CalificationModel)
- Clase: `CalificationModel`
- __tablename__: `califications`
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `FK_User_ID` — Integer, ForeignKey("users.Id")
  - `Average` — Float
  - `IsApproved` — Boolean, default=True
- Relaciones:
  - `user` — relationship("UserModel", back_populates="califications")

---

### `uacs` (UACModel)
- Clase: `UACModel`
- __tablename__: `uacs`
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `Clave` — String(32), unique=True, nullable=False
  - `Nombre` — String(200), nullable=False
  - `Tipo` — String(32), nullable=True
  - `Creditos` — Integer, nullable=True
  - `Horas_Sem` — Integer, nullable=True
- Relaciones:
  - `items` — relationship("ReportCardItemModel", back_populates="uac")

---

### `report_cards` (ReportCardModel)
- Clase: `ReportCardModel`
- __tablename__: `report_cards`
- __table_args__:
  - UniqueConstraint("Identity_ID", "Periodo", name="uq_report_cards_identity_periodo")
  - Index("ix_report_cards_identity_periodo", "Identity_ID", "Periodo")
  - Index("ix_report_cards_periodo", "Periodo")
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `Identity_ID` — Integer, ForeignKey("identities.Id"), nullable=False
  - `Periodo` — String(64), nullable=False
  - `Plan_Estudios` — String(120), nullable
  - `Carrera` — String(150), nullable
  - `Avance_Oblig` — Integer, default=0
  - `Avance_Opt` — Integer, default=0
  - `Avance_Total` — Integer, default=0
  - `Promedio` — Numeric(4,2), default=0
  - `Src_SHA256` — String(64), nullable=True
  - `Created_At` — DateTime(timezone=True), server_default=func.sysdatetime()
  - `Updated_At` — DateTime(timezone=True), server_default=func.sysdatetime(), onupdate=func.sysdatetime()
- Relaciones:
  - `identity` — relationship("IdentityModel", back_populates="report_cards")
  - `items` — relationship("ReportCardItemModel", back_populates="report_card", cascade="all, delete-orphan")

---

### `report_card_items` (ReportCardItemModel)
- Clase: `ReportCardItemModel`
- __tablename__: `report_card_items`
- __table_args__:
  - UniqueConstraint("ReportCard_ID", "Clave_UAC", "Semestre", name="uq_rci_rc_clave_sem")
  - Index("ix_rci_reportcard", "ReportCard_ID")
  - Index("ix_rci_clave", "Clave_UAC")
  - Index("ix_rci_semestre", "Semestre")
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `ReportCard_ID` — Integer, ForeignKey("report_cards.Id"), nullable=False
  - `UAC_ID` — Integer, ForeignKey("uacs.Id"), nullable=True
  - `Clave_UAC` — String(32), nullable=False
  - `Semestre` — Integer, nullable=False
  - `Nombre` — String(200), nullable=False
  - `Tipo_UAC` — String(32), nullable=True
  - `Calificacion` — Numeric(4,2), nullable=True
  - `Horas_Sem` — Integer, nullable=True
  - `Creditos` — Integer, nullable=True
  - `Periodo_Item` — String(64), nullable=True
- Relaciones:
  - `report_card` — relationship("ReportCardModel", back_populates="items")
  - `uac` — relationship("UACModel", back_populates="items")

---

### `report_card_raw` (ReportCardRawModel)
- Clase: `ReportCardRawModel`
- __tablename__: `report_card_raw`
- __table_args__:
  - UniqueConstraint("SHA256", name="uq_rcr_sha256")
- Columnas:
  - `Id` — Integer, primary_key, autoincrement
  - `Identity_ID` — Integer, ForeignKey("identities.Id"), nullable=False
  - `Periodo` — String(64), nullable=False
  - `Raw_JSON` — Text, nullable=False
  - `SHA256` — String(64), nullable=False
  - `Stored_URI` — String(400), nullable=True
  - `Created_At` — DateTime(timezone=True), server_default=func.sysdatetime()
- Relaciones:
  - `identity` — relationship("IdentityModel", back_populates="raw_report_cards")

---

### Base
- Archivo: `infrastructure/persistence/models/base.py`
- Clase: `Base` (DeclarativeBase)

---

## Observaciones
- Varias columnas no declaran explícitamente `nullable=`; si necesitas NOT NULL estricto, conviene declararlo.
- Índices y UniqueConstraints están declarados en `report_cards`, `report_card_items` y `report_card_raw`.

## Próximos pasos sugeridos
- Exportar a JSON (ya creado junto a este MD).
- Generar diagrama ER (PlantUML y Mermaid) — archivos creados en `reports/`.

Fin del informe.
