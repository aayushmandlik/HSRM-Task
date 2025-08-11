from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user_schema import UserRegister, UserOut
from schemas.token_schema import TokenResponse
from repositories import user_repository
from core.security import create_access_token, create_refresh_token
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str):
    return pwd_context.hash(password)

async def register_user(user: UserRegister):
    existing = await user_repository.find_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(user.password)
    user_dict = {**user.dict(), "password": hashed, "role": "user"}
    new_user = await user_repository.insert_user(user_dict)
    return UserOut(
        id=str(new_user["_id"]),
        name=new_user["name"],
        email=new_user["email"],
        message="User Registered Successfully"
    )

async def login_user(form_data: OAuth2PasswordRequestForm):
    record = await user_repository.find_user_by_email(form_data.username)
    if not record:
        raise HTTPException(status_code=404, detail="Email Not Found")
    if not verify_password(form_data.password, record["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "user_id": str(record["_id"]),
        "email": record["email"],
        "role": record.get("role", "user"),
        "name": record["name"]
    }

    return TokenResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
        email=record["email"],
        name=record["name"],
        role=record.get("role", "user"),
        user_id=str(record["_id"])
    )
