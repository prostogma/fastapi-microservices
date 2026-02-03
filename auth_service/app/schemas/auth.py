from pydantic import BaseModel, EmailStr

class AuthSchema(BaseModel):
    username: EmailStr  # email
    password: str

class UserAccessSchema(BaseModel):
    sub: str
    email: EmailStr
    is_verified: bool
    
class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "Bearer"