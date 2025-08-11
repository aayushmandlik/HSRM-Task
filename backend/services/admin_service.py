from fastapi import HTTPException
from core.config import ADMIN_VERIFICATION_CODE
from passlib.context import CryptContext
from repositories import admin_repository, user_repository
from core.security import create_access_token, create_refresh_token, require_admin
from schemas.admin_schema import AdminRegister, AdminLogin
from schemas.token_schema import TokenResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str):
    return pwd_context.hash(password)

async def register_admin(admin: AdminRegister):
    if admin.code != ADMIN_VERIFICATION_CODE:
        raise HTTPException(status_code=403, detail="Invalid verification code")

    existing = await admin_repository.find_admin_by_email(admin.email)
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")

    hashed = hash_password(admin.password)
    await admin_repository.insert_admin({**admin.dict(), "password": hashed})
    return {"message": "Admin registered"}

async def login_admin(admin: AdminLogin):
    record = await admin_repository.find_admin_by_email(admin.email)
    if not record:
        raise HTTPException(status_code=404, detail="Email Not Found")
    if not verify_password(admin.password, record["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "user_id": str(record["_id"]),
        "email": record["email"],
        "role": "admin",
        "name": record["name"]
    }
    return TokenResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        token_type="bearer",
        role="admin",
        email=record["email"],
        name=record["name"],
        user_id=str(record["_id"])
    )

async def admin_dashboard(current_admin):
    return {"message": f"Welcome Admin {current_admin['email']}"}

async def get_all_users():
    users_cursor = user_repository.find_all_users()
    users = []
    async for user in users_cursor:
        users.append({
            "user_id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user.get("role", "user")
        })
    return users

async def get_all_registered_users_and_admins():
    users_cursor = await user_repository.find_all_users()
    admins_cursor = await admin_repository.find_all_admins()
    combined = []

    async for user in users_cursor:
        combined.append({
            "user_id": str(user["_id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user.get("role", "user")
        })

    async for admin in admins_cursor:
        combined.append({
            "user_id": str(admin["_id"]),
            "email": admin["email"],
            "name": admin["name"],
            "role": admin.get("role", "admin")
        })

    return combined