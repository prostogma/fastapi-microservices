from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class AuthSchema(BaseModel):
    username: EmailStr   # email
    password: str = Field(max_length=50)

class CredentialCreateSchema(BaseModel):
    user_id: UUID
    password_hash: str

class UserAccessSchema(BaseModel):
    sub: str
    
class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"