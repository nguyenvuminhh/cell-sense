from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.schemas import BaseSchema

if TYPE_CHECKING:
    from server.schemas import UserSchema


class FreeUserQuotaSchema(BaseSchema):
    __tablename__ = "free_user_quota"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    free_quota_remaining: Mapped[int] = mapped_column(nullable=False)
    next_reset: Mapped[datetime] = mapped_column(nullable=False)

    # Relationships
    user: Mapped["UserSchema"] = relationship(
        "UserSchema",
        back_populates="free_user_quota",
        init=False,
    )
