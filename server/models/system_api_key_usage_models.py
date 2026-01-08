from datetime import date

from pydantic import BaseModel

from server.models import BaseSchemaInPydantic


class SystemApiKeyUsageRequest(BaseModel):
    date: date
    count: int = 0


class SystemApiKeyUsage(BaseSchemaInPydantic, SystemApiKeyUsageRequest):
    pass
