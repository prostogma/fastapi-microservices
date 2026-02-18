from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class AuthSchema(BaseModel):
    username: EmailStr   # email
    password: str = Field(max_length=50)

class CredentialCreateSchema(BaseModel):
    user_id: str
    password_hash: str

class UserAccessSchema(BaseModel):
    sub: str
    
class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
    
class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=100, description="От 8 до 100 символов")