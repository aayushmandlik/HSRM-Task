from datetime import datetime, timedelta
from jose import jwt, JWTError
from core.config import SECRET_KEY, ALGORITHM


# DATABASE_URL = "mongodb+srv://aayushmandlik:Aayush@123@cluster0.beiyj9c.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# MONGO_INITDB_DATABASE="hrms_db"
# SECRET_KEY="AuthenticationKey"
# ALGORITHM="HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES=60
# ADMIN_VERIFICATION_CODE="HARDCODED123"


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
