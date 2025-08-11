from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user_schema import UserLogin, UserRegister, UserOut
from schemas.token_schema import TokenResponse, TokenPayload
from core.security import get_current_user
from services import user_service

router = APIRouter(prefix='/api/users', tags=['User'])

@router.post("/register", response_model=UserOut)
async def register(user: UserRegister):
    return await user_service.register_user(user)

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await user_service.login_user(form_data)

@router.get("/profile")
async def get_profile(current_user: TokenPayload = Depends(get_current_user)):
    return {"message": "Welcome", "user": current_user.dict()}