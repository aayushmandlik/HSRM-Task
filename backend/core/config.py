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


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
MONOGO_URI = settings.DATABASE_URL
ADMIN_VERIFICATION_CODE = settings.ADMIN_VERIFICATION_CODE
