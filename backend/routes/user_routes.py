from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from databases.database import users_collection
from schemas.user_schema import UserLogin, UserRegister, UserOut
from schemas.token_schema import TokenResponse, TokenPayload
from passlib.context import CryptContext
from core.security import create_access_token, create_refresh_token, get_current_user
from typing import List

router = APIRouter(prefix='/api/users', tags=['User'])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/register", response_model=UserOut)
async def register(user: UserRegister):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = pwd_context.hash(user.password)
    user_dict = {**user.dict(), "password": hashed, "role": "user"}
    result = await users_collection.insert_one(user_dict)
    new_user = await users_collection.find_one({"_id": result.inserted_id})
    return UserOut(
        id=str(new_user["_id"]),
        name=new_user["name"],
        email=new_user["email"],
        message="User Registered Successfully"
    )

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    record = await users_collection.find_one({"email": form_data.username})
    if not record or not pwd_context.verify(form_data.password, record["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": str(record["_id"]),
        "email": record["email"],
        "role": record.get("role", "user"),
        "name": record["name"]
    })

    refresh_token = create_refresh_token({
        "user_id": str(record["_id"]),
        "email": record["email"],
        "role": record.get("role", "user"),
        "name": record["name"]
    })

    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "email": record["email"],
        "name": record["name"],
        "role": record.get("role", "user"),
        "user_id": str(record["_id"])
    }

@router.get("/profile")
async def get_profile(current_user: TokenPayload = Depends(get_current_user)):
    return {"message": "Welcome", "user": current_user.dict()}