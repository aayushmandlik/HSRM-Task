from fastapi import APIRouter, HTTPException, Depends
from schemas.admin_schema import AdminRegister, AdminLogin
from schemas.token_schema import TokenResponse, TokenPayload
from services import admin_service
from typing import List

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.post("/register")
async def register(admin: AdminRegister):
    return await admin_service.register_admin(admin)

@router.post("/login", response_model=TokenResponse)
async def login(admin: AdminLogin):
    return await admin_service.login_admin(admin)

@router.get("/dashboard")
async def dashboard(current_admin: TokenPayload = Depends(admin_service.require_admin)):
    return await admin_service.admin_dashboard(current_admin)

@router.get("/getallusers", response_model=List[TokenPayload])
async def get_all_users(current_admin: TokenPayload = Depends(admin_service.require_admin)):
    return await admin_service.get_all_users()

@router.get("/getallregistereduseradmin", response_model=List[TokenPayload])
async def get_all_registered(current_admin: TokenPayload = Depends(admin_service.require_admin)):
    return await admin_service.get_all_registered_users_and_admins()