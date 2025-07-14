from fastapi import APIRouter,HTTPException,Depends
from databases.database import users_collection
from schemas.user_schema import UserLogin,UserRegister
from schemas.token_schema import TokenResponse
from passlib.context import CryptContext
from core.security import create_access_token,verify_token,create_refresh_token,get_current_user
from typing import List
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

router = APIRouter(prefix='/api/users', tags=['User'])
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/users/login')

# blacklisted_tokens: List[str] = []

# Verify hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Get current user using JWT
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     payload = verify_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     return payload


def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access only")
    return current_user

@router.post("/register")
async def register(user: UserRegister):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400,detail="User Already exists")
    hashed = pwd_context.hash(user.password)
    await users_collection.insert_one({**user.dict(),"password":hashed})
    return {"message":"User Registered"}

# @router.post("/login",response_model=TokenResponse)
# async def login(user: UserLogin):
#     record = await users_collection.find_one({"email":user.email})
#     if not record or not pwd_context.verify(user.password,record["password"]):
#         raise HTTPException(status_code=401,detail="Invalid Credentials")
#     token = create_access_token({"email":record["email"], "role":"user", "name":record["name"]})
#     return {"token":token, "role":"user", "email":record["email"], "name":record["name"]}

# @router.post('/login',response_model=TokenResponse)
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user_record = await users_collection.find_one({"email": form_data.username})
#     if not user_record or not verify_password(form_data.password, user_record["password"]):
#         raise HTTPException(status_code=400, detail="Invalid credentials")

#     data = {"email": user_record["email"], "role": "user", "name":user_record["name"]}
#     access_token = create_access_token(data)
#     refresh_token = create_refresh_token(data)
#     return {"access_token":access_token, "role":"user", "email":user_record["email"], "name":user_record["name"],"token_type":"bearer"}
#     # return {"access_token":access_token,"token_type": "bearer"}

@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):  # Expects JSON: { "email": "...", "password": "..." }
    record = await users_collection.find_one({"email": user.email})
    if not record or not pwd_context.verify(user.password, record["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"email": record["email"], "role": "user", "name": record["name"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "email": record["email"],
        "name": record["name"],
        "role": "user"
    }


@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {"message": "Welcome", "user": current_user}
