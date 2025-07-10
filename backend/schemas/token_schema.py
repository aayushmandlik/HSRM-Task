from pydantic import BaseModel

class TokenResponse(BaseModel):
    token: str
    role: str
    email: str
    name: str