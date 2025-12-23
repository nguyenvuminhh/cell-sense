from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.schemas import BaseSchema

if TYPE_CHECKING:
    from server.schemas import ChatSchema, FreeUserQuotaSchema


class UserSchema(BaseSchema):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    email: Mapped[str] = mapped_column(nullable=False)
    gemini_api_key: Mapped[str] = mapped_column(nullable=True)

    # Relationships
    chats: Mapped[list["ChatSchema"]] = relationship(
        "ChatSchema",
        back_populates="user",
        cascade="all, delete-orphan",
        init=False,
    )

    free_user_quota: Mapped["FreeUserQuotaSchema"] = relationship(
        "FreeUserQuotaSchema",
        back_populates="user",
        cascade="all, delete-orphan",
        init=False,
        uselist=False,
    )
