from sqlalchemy.orm import Session
from infrastructure.persistence.models.user_model import UserModel
def get_user_count(db: Session) -> int:
    """Devuelve la cantidad total de usuarios registrados."""
    return db.query(UserModel).count()
