from typing import Annotated
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as SQLUUID

from app.db.base import Base, limited_string
from app.db.enums import PendingStatusEnum


class Notification(Base):
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(SQLUUID())
    template_id: Mapped[UUID] = mapped_column(ForeignKey("templates.id"))
    recipient_email: Mapped[limited_string]
    verification_token: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[PendingStatusEnum] = mapped_column(default=PendingStatusEnum.pending)
    attempts: Mapped[int] = mapped_column(default=0)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    template: Mapped["Template"] = relationship(
        "Template",
        back_populates="notifications"
    )


class Template(Base):
    __tablename__ = "templates"

    name: Mapped[limited_string]
    subject: Mapped[limited_string]
    body: Mapped[str | None]
    
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="template"
    )
