from datetime import datetime, timedelta, timezone

from fastapi import Request
from fastapi.responses import JSONResponse

from server.config import MAX_TIMESTAMP_DIFF_SECONDS, SKIP_AUTH_PATHS


async def verify_timestamps(request: Request, call_next):
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
        or diff.total_seconds() < -10
    ):
        return JSONResponse(
            {
                "detail": f"Timestamp too old or from the future. Diff: {diff.total_seconds()} seconds"
            },
            status_code=401,
        )

    return await call_next(request)
