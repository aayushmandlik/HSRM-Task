# from fastapi import APIRouter, HTTPException,Depends
# from databases.database import admins_collection
# from schemas.admin_schema import AdminRegister, AdminLogin
# from core.config import ADMIN_VERIFICATION_CODE
# from core.security import create_access_token,require_admin
# from passlib.context import CryptContext
# from schemas.token_schema import TokenResponse

# router = APIRouter(prefix="/api/admin", tags=["Admin"])
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# @router.post("/register")
# async def register(admin: AdminRegister):
#     if admin.code != ADMIN_VERIFICATION_CODE:
#         raise HTTPException(status_code=403, detail="Invalid verification code")

#     existing = await admins_collection.find_one({"email": admin.email})
#     if existing:
#         raise HTTPException(status_code=400, detail="Admin already exists")
#     hashed = pwd_context.hash(admin.password)
#     await admins_collection.insert_one({**admin.dict(), "password": hashed})
#     return {"message": "Admin registered"}

# @router.post("/login", response_model=TokenResponse)
# async def login(admin: AdminLogin):
#     record = await admins_collection.find_one({"email": admin.email})
#     if not record or not pwd_context.verify(admin.password, record["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
    
#     token = create_access_token({"email": record["email"], "role": "admin", "name": record["name"]})
#     return {"token": token, "role": "admin", "email": record["email"], "name": record["name"]}

# @router.get('/dashboard')
# def get_dashboard(current_user: dict = Depends(require_admin)):
#     return {"message": f"Welcome Admin {current_user["name"]}",
#             "email":current_user["email"],
#             "role": current_user["role"]}

from fastapi import APIRouter, HTTPException, Depends
from databases.database import admins_collection
from schemas.admin_schema import AdminRegister, AdminLogin
from core.config import ADMIN_VERIFICATION_CODE
from core.security import create_access_token,require_admin
from passlib.context import CryptContext
from schemas.token_schema import TokenResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def register(admin: AdminRegister):
    if admin.code != ADMIN_VERIFICATION_CODE:
        raise HTTPException(status_code=403, detail="Invalid verification code")

    existing = await admins_collection.find_one({"email": admin.email})
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")
    hashed = pwd_context.hash(admin.password)
    await admins_collection.insert_one({**admin.dict(), "password": hashed})
    return {"message": "Admin registered"}

@router.post("/login", response_model=TokenResponse)
async def login(admin: AdminLogin):
    record = await admins_collection.find_one({"email": admin.email})
    if not record or not pwd_context.verify(admin.password, record["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": str(record["_id"]),"email": record["email"], "role": "admin", "name": record["name"]})
    return {"access_token": token,"token_type":"bearer", "role": "admin", "email": record["email"], "name": record["name"],"user_id": str(record["_id"])}


@router.get("/dashboard")
async def dashboard(current_admin: dict = Depends(require_admin)):
    return {"message": f"Welcome Admin {current_admin['email']}"}

