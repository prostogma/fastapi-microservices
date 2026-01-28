from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String, func, Index

from app.db.base import Base


class Credential(Base):
    __tablename__ = "credentials"

    id: Mapped[UUID] = mapped_column(SQLUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(SQLUUID, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    password_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(SQLUUID, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(SQLUUID)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    __table_args__ = (
        Index("idx_refresh_token_hash", "token_hash", unique=True),
    )
