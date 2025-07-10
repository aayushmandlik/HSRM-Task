# import os 
# from dotenv import load_dotenv


from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MONGO_INITDB_DATABASE: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    ADMIN_VERIFICATION_CODE: str

    class Config:
        env_file = './.env'


settings = Settings()


# load_dotenv()

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
# MONGO_URI = os.getenv("MONGO_URI")
# ADMIN_VERIFICATION_CODE = os.getenv("ADMIN_VERIFICATION_CODE")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
MONOGO_URI = settings.DATABASE_URL
ADMIN_VERIFICATION_CODE = settings.ADMIN_VERIFICATION_CODE
