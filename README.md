# CETMAR_41_BACK
Repository for the development of the grade management system.

---

## 🛠 Requirements

- **Python**: Version >= 3.13  
[Download Python](https://www.python.org/downloads/)

- **SQL Server** (local or remote instance)  
  - Make sure you have **SQL Server** running and the **ODBC Driver 17/18** installed.  
  - Example download: [ODBC Driver for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

- **Virtual Environment** (recommended)

---

## Clone the Repository

```
git init .
git remote add origin https://github.com/GuillermoSM33/CETMAR_41_BACK.git
git branch -m main
git fetch
git pull origin main
```

Now you can see the project in your path

---

# Create and Activate Virtual Environment

```
python -m venv .venv
```

Activate it:

Windows PowerShell

```
.venv\Scripts\Activate.ps1
```

Linux/Mac

```
source .venv/bin/activate
```

---

# How to install the project requirements?

```
pip install -r requirements.txt
```

---

# Environment Variables

Create a .env file in the project root with your database connection string. Example:

```
DATABASE_URL="mssql+pyodbc://USERNAME:PASSWORD@SERVERNAME/DBNAME?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
```

Replace USERNAME, PASSWORD, SERVERNAME, DBNAME with your own values.

---

# Database & Migrations

The project uses Alembic for database migrations.

## Reset migrations (create schema from 0)

If you want to rebuild the database schema from scratch (recommended when you reset Alembic history):

1. Create a **new empty database** (or drop all tables, including `alembic_version`).
2. Ensure your `.env` has a valid `DATABASE_URL`.
3. Apply the baseline migration:

```
alembic upgrade head
```

If you already have a database with the schema created, but Alembic revision history changed (you get a “Can't locate revision” error), you can align the version table without running migrations:

```
alembic stamp head
```

1. Create a new migration (after modifying models)

```
alembic revision --autogenerate -m "your migration message"
```

2. Apply migrations to the database

```
alembic upgrade head
```

3. (Optional) Rollback last migration

```
alembic downgrade -1
```

---

# Seeding Dummy Data

To populate the database with initial data for testing:

```
python -m infrastructure.seeds.seed
```

This will insert default roles, some users, and tokens.

---

# Run the Project

```
uvicorn app.main:app --reload
```

Then open http://localhost:8000
 to access the API.

---

# Notes

Use Alembic for schema changes (never edit the database manually).

Use seeds only in development. Production environments should only insert catalog data (like roles) through migrations.

---

# Contributions

Would you like to contribute? First, you should learn the basic structure for making better commits and improving workflow.

Please read the next part for learn how work in your own branch :D

---

# Branches

Every new feature, bug fix, or improvement must be created in a new branch.
The branch naming convention is:

Type_Module_Description

Common types:

1- Feature_ → New functionality

2- Fix_ or Hotfix_ → Bug fixes

3- Refactor_ → Code improvements without adding features

4- Docs_ → Documentation changes

Examples:
Feature_Auth_Base
Feature_Auth_JWT
Feature_Grades_CRUD
Hotfix_Login_Bug
Refactor_UserService

---

# Commits

Commits must follow this structure:

TYPE(MODULE): Short description of the change

Types of commits:

1- FEAT → New features

2- FIX → Bug fixes

3- REFACTOR → Code improvements

4- DOCS → Documentation changes

Examples:

FEAT(AUTH): Added base authentication with SQLAlchemy
FEAT(AUTH): Implemented JWT for login
FIX(AUTH): Fixed bug in password validation
REFACTOR(GRADES): Extracted business logic from controller
DOCS(README): Added environment variables example

---

# Workflow Example

Create a new branch from main:

```
git checkout main
git pull origin main
git checkout -b Feature_Auth_JWT
```

Make your changes, then stage files:

```
git add .
```

Commit with a clear message:

```
git commit -m "FEAT(AUTH): Implemented JWT for login"
```

Push your branch:

```
git push origin Feature_Auth_JWT
```

---

# Main Branches

Open a Pull Request (PR) to merge into main branches.
