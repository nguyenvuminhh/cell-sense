from datetime import datetime, timedelta, timezone

from fastapi import Request
from fastapi.responses import JSONResponse

from server.config import MAX_TIMESTAMP_DIFF_SECONDS, SKIP_AUTH_PATHS


async def verify_timestamps(request: Request, call_next):
    """
    Middleware to verify that the request contains a valid `timestamp`
    query parameter in ISO8601 format (e.g., 2025-11-18T09:12:55.123Z).

    Rejects requests older than 1 minutes to prevent replay attacks.
    """
    if any(request.url.path.startswith(path) for path in SKIP_AUTH_PATHS):
        return await call_next(request)
    timestamp = request.query_params.get("timestamp")
    if timestamp is None:
        return JSONResponse(
            {"detail": "Missing timestamp query parameter."}, status_code=400
        )

    try:
        # Parse ISO 8601 with Z → UTC
        timestamp_iso = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return JSONResponse(
            {"detail": "Invalid timestamp format. Use ISO8601."},
            status_code=400,
        )

    now = datetime.now(timezone.utc)
    diff = now - timestamp_iso

    # Validate recency
    if (
        diff > timedelta(seconds=MAX_TIMESTAMP_DIFF_SECONDS)
        or diff.total_seconds() < 0
    ):
        return JSONResponse(
            {"detail": "Timestamp too old or from the future."}, status_code=401
        )

    return await call_next(request)
