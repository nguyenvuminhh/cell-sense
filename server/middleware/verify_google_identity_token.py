from fastapi import Request
from fastapi.responses import JSONResponse
from google.auth.transport import requests
from google.oauth2 import id_token

from server.config import ENV, GOOGLE_OAUTH_CLIENT_ID, SKIP_AUTH_PATHS
from server.constants import Environments


async def verify_google_identity_token(request: Request, call_next):
    """Verify Google identity token from Apps Script."""
    if ENV == Environments.TEST:
        return await call_next(request)

    if any(request.url.path.startswith(path) for path in SKIP_AUTH_PATHS):
        return await call_next(request)

    authorization = request.headers.get("Authorization")
    if not authorization:
        return JSONResponse(
            {"detail": "Missing Authorization header"}, status_code=401
        )

    if not authorization.startswith("Bearer "):
        return JSONResponse(
            {"detail": "Invalid Authorization header format"}, status_code=401
        )

    token = authorization.replace("Bearer ", "")

    try:
        # Verifies signature, expiry, issuer automatically
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=GOOGLE_OAUTH_CLIENT_ID,
        )

        # Store user info in request state for downstream handlers
        request.state.google_user = {
            "email": id_info.get("email"),
            "email_verified": id_info.get("email_verified"),
            "aud": id_info.get("aud"),
            "iss": id_info.get("iss"),
            "exp": id_info.get("exp"),
            "sub": id_info.get("sub"),
        }

    except ValueError as e:
        return JSONResponse(
            {"detail": f"Invalid identity token: {str(e)}"}, status_code=401
        )

    return await call_next(request)
