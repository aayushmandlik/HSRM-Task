from fastapi import APIRouter,HTTPException
from databases.database import users_collection
from schemas.userSchema import UserLogin,UserRegister
from schemas.token_schema import TokenResponse
from passlib.context import CryptContext
from core.security import create_access_token

router = APIRouter(prefix='/users', tags=['User'])
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

@router.post("/register")
async def register(user: UserRegister):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400,detail="User Already exists")
    hashed = pwd_context.hash(user.password)
    await users_collection.insert_one({**user.dict(),"password":hashed})
    return {"message":"User Registered"}

@router.post("/login",response_model=TokenResponse)
async def login(user: UserLogin):
    record = await users_collection.find_one({"email":user.email})
    if not record or not pwd_context.verify(user.password,record["password"]):
        raise HTTPException(status_code=401,detail="Invalid Credentials")
    token = create_access_token({"email":record["email"], "role":"user", "name":record["name"]})
    return {"token":token, "role":"user", "email":record["email"], "name":record["name"]}
