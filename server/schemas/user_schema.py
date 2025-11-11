from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from server.utils import BaseSchema


class UserSchema(BaseSchema):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    email: Mapped[str] = mapped_column(nullable=False)
    gemini_api_key: Mapped[str] = mapped_column(nullable=True)
