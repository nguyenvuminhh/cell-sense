# server/middleware/verify_apps_script.py

from fastapi import Request
from fastapi.responses import JSONResponse

from server.config import SKIP_AUTH_PATHS
from server.utils.verify_signature import verify_signature


async def verify_signature_from_apps_script(request: Request, call_next):
    if any(request.url.path.startswith(path) for path in SKIP_AUTH_PATHS):
        return await call_next(request)
    signature_b64 = request.headers.get("X-Signature")
    if not signature_b64:
        return JSONResponse(
            {"detail": "Missing X-Signature header"}, status_code=401
        )

    full_url = str(request.url)

    try:
        body_bytes = await request.body()
        payload = {} if not body_bytes else await request.json()
    except Exception:
        return JSONResponse({"detail": "Invalid JSON body"}, status_code=400)

    # IMPORTANT: We need to re-inject the body into the request,
    # otherwise downstream handlers won't receive it.
    async def receive_again():
        return {"type": "http.request", "body": body_bytes}

    request._receive = receive_again

    valid = verify_signature(payload, full_url, signature_b64)

    if not valid:
        return JSONResponse({"detail": "Invalid signature"}, status_code=401)

    return await call_next(request)
