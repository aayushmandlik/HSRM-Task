from pymongo import MongoClient
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

users_collection = db['users']
admins_collection = db['admin']
employee_collection = db['employees']
task_collection = db['tasks']
attendance_collection = db['attendance']
leave_collection = db['leaves']
payroll_collection = db['payrolls']