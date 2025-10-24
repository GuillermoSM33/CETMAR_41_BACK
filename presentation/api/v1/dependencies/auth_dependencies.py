from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from infrastructure.config.settings import settings

bearer_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return {
            "id": int(payload.get("sub")) if payload.get("sub") else None,
            "role_name": payload.get("role") or payload.get("rol") or payload.get("role_name")
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

def admin_required(current_user=Depends(get_current_user)):
    role = (current_user.get("role_name") or "").lower()
    if role not in ("director", "admin", "management_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado.")
    return current_user