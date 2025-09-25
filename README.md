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
