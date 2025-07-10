from pymongo import MongoClient
import pymongo
from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str

    class Config:
        env_file = './.env'


settings = Settings()

conn = MongoClient(settings.DATABASE_URL)
db = conn[settings.MONGO_INITDB_DATABASE]

# uri = "mongodb+srv://aayushmandlik:Aayush@123@cluster0.beiyj9c.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# conn = MongoClient(uri)
# db = conn.HSRM

users_collection = db['users']
admins_collection = db['admin']