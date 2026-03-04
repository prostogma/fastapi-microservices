from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.crud.users import create_user, deactivate_user, update_user
from app.db.models import User


