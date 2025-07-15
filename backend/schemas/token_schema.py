from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str
    name: str
    user_id: str

class TokenPayload(BaseModel):
    user_id: str
    role: str
    name: str
    email: str
    exp: int