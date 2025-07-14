# from datetime import datetime, timedelta
# from jose import jwt, JWTError
# from core.config import SECRET_KEY, ALGORITHM
# from fastapi import Depends,HTTPException,status
# from fastapi.security import OAuth2PasswordBearer
# from jose import jwt,JWTError


# # DATABASE_URL = "mongodb+srv://aayushmandlik:Aayush@123@cluster0.beiyj9c.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# # MONGO_INITDB_DATABASE="hrms_db"
# # SECRET_KEY="AuthenticationKey"
# # ALGORITHM="HS256"
# # ACCESS_TOKEN_EXPIRE_MINUTES=60
# # ADMIN_VERIFICATION_CODE="HARDCODED123"

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# def verify_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except JWTError:
#         return None

# # def verify_token(token: str = Depends(oauth2_scheme)):
# #     credentials_exception = HTTPException(status_code=401,detail="Invalid Token",headers={"WWW-Authenticate": "Bearer"},)
# #     try:
# #         payload =  jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
# #         return payload
# #     except JWTError:
# #         raise credentials_exception
    

# # def get_current_user(current_user: dict = Depends(verify_token)):
# #     return current_user

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     print("Token Received: ",token)
#     payload = verify_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return payload

# def require_admin(current_user: dict = Depends(get_current_user)):
#     if current_user.get("role") != "admin":
#         raise HTTPException(status_code=403, details="Admin Access Only") 
#     return current_user




from datetime import datetime, timedelta
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM


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

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        return payload
    except JWTError:
        return None



bearer_scheme = HTTPBearer(auto_error=False)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(payload=Depends(verify_token)):
    if payload.get("role") != "user":
        raise HTTPException(status_code=403, detail="User access only")
    return payload

def require_admin(payload=Depends(verify_token)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    return payload

def require_admin_or_user(payload=Depends(verify_token)):
    role = payload.get("role")
    if role not in ["user","admin"]:
        raise HTTPException(status_code=403,detail="Access Denied")
    return payload