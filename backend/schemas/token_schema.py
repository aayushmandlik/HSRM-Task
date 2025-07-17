from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    email: str
    name: str
    role: str
    user_id: str

class TokenPayload(BaseModel):
    user_id: str
    email: str
    role: str
    name: str