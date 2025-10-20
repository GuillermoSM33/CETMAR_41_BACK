from alembic import op
import sqlalchemy as sa
import bcrypt

# revision identifiers, used by Alembic.
revision = '7488558f8abc'
down_revision = '2c0fc9c02228'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Crear tabla
    op.create_table(
        'passwords',
        sa.Column('Id', sa.Integer(), autoincrement=True, primary_key=True, nullable=False),
        sa.Column('FK_User_ID', sa.Integer(), nullable=False, unique=True),
        sa.Column('Hashed_Password', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['FK_User_ID'], ['users.Id'])
    )

    # Insertar contraseñas dummy para todos los usuarios existentes, las contrseñas son del 1 al 6
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT Id FROM users"))
    users = result.fetchall()

    for user in users:
        hashed = bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode('utf-8')
        connection.execute(
            sa.text(
                "INSERT INTO passwords (FK_User_ID, Hashed_Password) VALUES (:user_id, :password)"
            ),
            {"user_id": user.Id, "password": hashed}
        )

def downgrade() -> None:
    op.drop_table('passwords')
