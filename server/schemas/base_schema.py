from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
)


class BaseSchema(DeclarativeBase, MappedAsDataclass):
    # Automatically set when record is first created
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, init=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
        nullable=False,
        init=False,
    )

    # Automatically updated whenever record changes
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )
