import datetime

from sqlalchemy.orm import Mapped, mapped_column

from server.schemas import BaseSchema


class SystemApiKeyUsageSchema(BaseSchema):
    __tablename__ = "system_api_key_usage"

    date: Mapped[datetime.date] = mapped_column(nullable=False, unique=True)
    count: Mapped[int] = mapped_column(nullable=False, default=0)
