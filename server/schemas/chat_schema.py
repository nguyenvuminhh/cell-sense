from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.constants import DEFAULT_CHAT_NAME
from server.schemas import BaseSchema

if TYPE_CHECKING:
    from server.schemas import ChatMessageSchema, UserSchema


class ChatSchema(BaseSchema):
    __tablename__ = "chats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(
        nullable=False,
        default=DEFAULT_CHAT_NAME,
        server_default=DEFAULT_CHAT_NAME,
        init=False,
    )

    # Relationships
    user: Mapped["UserSchema"] = relationship(
        "UserSchema",
        back_populates="chats",
        init=False,
    )
    messages: Mapped[list["ChatMessageSchema"]] = relationship(
        "ChatMessageSchema",
        back_populates="chat",
        cascade="all, delete-orphan",
        init=False,
    )


class ChatMessageSchema(BaseSchema):
    __tablename__ = "chat_messages"
    __table_args__ = (
        sa.CheckConstraint(
            "is_from_user = true OR model_name IS NOT NULL",
            name="ck_chat_messages_model_name_required",
        ),
        sa.CheckConstraint(
            "CASE WHEN is_from_user = true THEN full_user_prompt IS NOT NULL ELSE full_model_response IS NOT NULL END",
            name="check_full_prompt_response",
        ),
    )

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    is_from_user: Mapped[bool] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str | None] = mapped_column(nullable=True)
    full_user_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_model_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Relationships
    chat: Mapped["ChatSchema"] = relationship(
        "ChatSchema",
        back_populates="messages",
        init=False,
    )
