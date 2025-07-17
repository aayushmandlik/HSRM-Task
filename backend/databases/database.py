from pymongo import MongoClient
# import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    class Config:
        env_file = './.env'


settings = Settings()

conn = AsyncIOMotorClient(settings.DATABASE_URL)
db = conn[settings.MONGO_INITDB_DATABASE]

# uri = "mongodb+srv://aayushmandlik:Aayush@123@cluster0.beiyj9c.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# conn = MongoClient(uri)
# db = conn.HSRM

users_collection = db['users']
admins_collection = db['admin']
employee_collection = db['employees']
task_collection = db['tasks']
attendance_collection = db['attendance']
leave_collection = db['leaves']
payroll_collection = db['payrolls']