from datetime import datetime

from pydantic import BaseModel

from server.models import BaseSchemaInPydantic


class FreeUserQuotaRequest(BaseModel):
    user_id: int
    free_quota_remaining: int
    next_reset: datetime


class FreeUserQuota(BaseSchemaInPydantic, FreeUserQuotaRequest):
    pass


class FreeUserQuotaUpdate(BaseModel):
    free_quota_remaining: int | None = None
    next_reset: datetime | None = None
