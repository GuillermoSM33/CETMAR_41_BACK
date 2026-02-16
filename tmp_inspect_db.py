import os
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import text

load_dotenv()
url = os.getenv('DATABASE_URL')
print('DATABASE_URL:', url)
engine = sa.create_engine(url, pool_pre_ping=True)

with engine.connect() as c:
    db = c.execute(text('select db_name()')).scalar_one()
    user = c.execute(text('select user_name()')).scalar_one()
    default_schema = c.execute(text("select default_schema_name from sys.database_principals where name = user_name()" )).scalar_one()
    print('DB:', db)
    print('USER:', user)
    print('DEFAULT_SCHEMA:', default_schema)

    uacs_tables = c.execute(text("""
        select s.name as schema_name, t.name as table_name
        from sys.tables t
        join sys.schemas s on s.schema_id = t.schema_id
        where t.name = 'uacs'
        order by s.name
    """)).fetchall()
    print('UACS tables:', uacs_tables)

    uacs_cols = c.execute(text("""
        select table_schema, column_name
        from information_schema.columns
        where table_name = 'uacs'
          and column_name in ('Creditos', 'Horas_Sem')
        order by table_schema, column_name
    """)).fetchall()
    print('UACS columns present:', uacs_cols)
