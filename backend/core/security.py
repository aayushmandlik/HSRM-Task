from datetime import datetime, timedelta
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM
from schemas.token_schema import TokenPayload


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



bearer_scheme = HTTPBearer(auto_error=False)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded Payload: ",payload)
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token/Try Login again")

def get_current_user(payload=Depends(verify_token)):
    if payload.get("role") != "user":
        raise HTTPException(status_code=403, detail="User access only")
    return payload

def require_admin(payload=Depends(verify_token)) -> TokenPayload:
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    return TokenPayload(**payload)

def require_admin_or_user(payload=Depends(verify_token)) -> TokenPayload:
    role = payload.get("role")
    if role not in ["user","admin"]:
        raise HTTPException(status_code=403,detail="Access Denied")
    return TokenPayload(**payload)