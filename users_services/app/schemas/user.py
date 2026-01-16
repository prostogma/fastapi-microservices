from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BaseUserSchema(BaseModel):
    email: EmailStr | None
    is_active: bool | None


class UserCreateSchema(BaseUserSchema):
    email: EmailStr
    is_active: bool | None = True


class UserOutSchema(BaseUserSchema):
    id: UUID
    is_verified: bool | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSchema(BaseUserSchema):
    email: EmailStr | None = None
    is_verified: bool | None = None
    is_active: bool | None = None

class SortBy(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    
class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"
    
class UsersListQuerySchema(BaseModel):
    limit: int = Field(default=20, gt=0, lt=100)
    offset: int = Field(default=0, ge=0)
    
    is_active: bool | None = None
    is_verified: bool | None = None
    
    sort_by: SortBy = Field(default=SortBy.CREATED_AT)
    sort_order: SortOrder = Field(SortOrder.DESC)
