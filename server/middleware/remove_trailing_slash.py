from fastapi import Request
from fastapi.responses import RedirectResponse


async def remove_trailing_slash(request: Request, call_next):
    path = request.url.path
    # Skip root and paths without trailing slash
    if path != "/" and path.endswith("/"):
        # Preserve query params if present
        new_url = str(request.url).rstrip("/")
        return RedirectResponse(url=new_url, status_code=301)
    return await call_next(request)
