from fastapi import FastAPI
from routes.user_routes import UserLogin,UserRegister
app = FastAPI()

app.include_router(UserLogin)
app.include_router(UserRegister)