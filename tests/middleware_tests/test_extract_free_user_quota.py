"""
Tests for extract_free_user_quota_from_request middleware.
"""

from datetime import datetime, time, timedelta

import pytest

from server import config
from server.crud import free_user_quota_crud, users_crud
from server.middleware.extract_free_user_quota_from_request import (
    extract_free_user_quota_from_request,
)
from server.models.free_user_quota_models import FreeUserQuotaRequest
from server.models.user_models import UserRequest


# Helper function to create a unique user for each test
async def create_test_user(
    session, email_suffix: str, api_key: str | None = None
):
    """Create a test user with unique email to avoid unique constraint violations."""
    user_request = UserRequest(
        email=f"test_quota_{email_suffix}@example.com",
        gemini_api_key=api_key,
    )
    user = await users_crud.create_user(session, user_request)
    return user


@pytest.mark.asyncio
async def test_extract_quota_existing_quota(db_session):
    """Test extracting an existing quota for a user."""
    # Create a user
    user = await create_test_user(db_session, "existing_quota")

    # Create quota for the user
    quota_request = FreeUserQuotaRequest(
        user_id=user.id,
        free_quota_remaining=5,
        next_reset=datetime.combine(datetime.today(), time(23, 59, 59)),
    )
    existing_quota = await free_user_quota_crud.create_free_user_quota(
        db_session, quota_request
    )
    await db_session.commit()

    # Extract the quota
    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    assert extracted_quota is not None
    assert extracted_quota.user_id == user.id
    assert extracted_quota.free_quota_remaining == 5
    assert extracted_quota.id == existing_quota.id


@pytest.mark.asyncio
async def test_extract_quota_creates_new_quota(db_session):
    """Test that a new quota is created if one doesn't exist."""
    # Create a user without quota
    user = await create_test_user(db_session, "new_quota")
    await db_session.commit()

    # Verify no quota exists
    existing = await free_user_quota_crud.get_free_user_quota_by_user_id(
        db_session, user.id
    )
    assert existing is None

    # Extract quota (should create new one)
    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    assert extracted_quota is not None
    assert extracted_quota.user_id == user.id
    assert extracted_quota.free_quota_remaining == config.FREE_USER_DAILY_QUOTA
    assert extracted_quota.next_reset is not None


@pytest.mark.asyncio
async def test_extract_quota_uses_default_quota_value(db_session):
    """Test that newly created quota uses the default quota value from config."""
    user = await create_test_user(db_session, "default_quota")
    await db_session.commit()

    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    assert extracted_quota.free_quota_remaining == config.FREE_USER_DAILY_QUOTA


@pytest.mark.asyncio
async def test_extract_quota_sets_next_reset_to_end_of_day(db_session):
    """Test that newly created quota has next_reset set to end of current day."""
    user = await create_test_user(db_session, "reset_time")
    await db_session.commit()

    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    expected_reset = datetime.combine(datetime.today(), time(23, 59, 59))
    assert extracted_quota.next_reset == expected_reset


@pytest.mark.asyncio
async def test_extract_quota_multiple_calls_same_user(db_session):
    """Test that multiple calls for same user return the same quota."""
    user = await create_test_user(db_session, "same_quota")
    await db_session.commit()

    # First call - creates quota
    quota1 = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )
    await db_session.commit()

    # Second call - retrieves existing quota
    quota2 = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    assert quota1.id == quota2.id
    assert quota1.user_id == quota2.user_id
    assert quota1.free_quota_remaining == quota2.free_quota_remaining


@pytest.mark.asyncio
async def test_extract_quota_different_users_different_quotas(db_session):
    """Test that different users have different quota records."""
    user1 = await create_test_user(db_session, "user1_quota")
    user2 = await create_test_user(db_session, "user2_quota")
    await db_session.commit()

    quota1 = await extract_free_user_quota_from_request(
        user=user1, session=db_session
    )
    await db_session.commit()

    quota2 = await extract_free_user_quota_from_request(
        user=user2, session=db_session
    )
    await db_session.commit()

    assert quota1.id != quota2.id
    assert quota1.user_id == user1.id
    assert quota2.user_id == user2.id


@pytest.mark.asyncio
async def test_extract_quota_respects_existing_quota_amount(db_session):
    """Test that existing quota amount is preserved when extracting."""
    user = await create_test_user(db_session, "preserved_quota")

    # Create quota with specific remaining amount
    custom_amount = 3
    quota_request = FreeUserQuotaRequest(
        user_id=user.id,
        free_quota_remaining=custom_amount,
        next_reset=datetime.combine(datetime.today(), time(23, 59, 59)),
    )
    await free_user_quota_crud.create_free_user_quota(db_session, quota_request)
    await db_session.commit()

    # Extract quota
    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    assert extracted_quota.free_quota_remaining == custom_amount


@pytest.mark.asyncio
async def test_extract_quota_with_zero_remaining(db_session):
    """Test extracting quota when remaining is zero."""
    user = await create_test_user(db_session, "zero_quota")

    # Create quota with zero remaining
    quota_request = FreeUserQuotaRequest(
        user_id=user.id,
        free_quota_remaining=0,
        next_reset=datetime.combine(datetime.today(), time(23, 59, 59)),
    )
    await free_user_quota_crud.create_free_user_quota(db_session, quota_request)
    await db_session.commit()

    # Extract quota
    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    assert extracted_quota.free_quota_remaining == 0


@pytest.mark.asyncio
async def test_extract_quota_resets_expired_quota(db_session):
    """Test that expired quota is reset when extracted."""
    user = await create_test_user(db_session, "expired_quota")

    # Create quota that expired yesterday
    yesterday = datetime.now() - timedelta(days=1)
    quota_request = FreeUserQuotaRequest(
        user_id=user.id,
        free_quota_remaining=0,  # Was depleted
        next_reset=datetime.combine(yesterday.date(), time(23, 59, 59)),
    )
    await free_user_quota_crud.create_free_user_quota(db_session, quota_request)
    await db_session.commit()

    # Extract quota (should reset)
    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    # Should be reset to default value
    assert extracted_quota.free_quota_remaining == config.FREE_USER_DAILY_QUOTA
    # Next reset should be today's end
    expected_reset = datetime.combine(datetime.today(), time(23, 59, 59))
    assert extracted_quota.next_reset == expected_reset


@pytest.mark.asyncio
async def test_extract_quota_does_not_reset_future_quota(db_session):
    """Test that quota with future reset date is not reset."""
    user = await create_test_user(db_session, "future_quota")

    # Create quota with future reset date
    future_reset = datetime.combine(datetime.today(), time(23, 59, 59))
    quota_request = FreeUserQuotaRequest(
        user_id=user.id,
        free_quota_remaining=5,
        next_reset=future_reset,
    )
    await free_user_quota_crud.create_free_user_quota(db_session, quota_request)
    await db_session.commit()

    # Extract quota
    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    # Should keep the original value
    assert extracted_quota.free_quota_remaining == 5


@pytest.mark.asyncio
async def test_extract_quota_returns_complete_model(db_session):
    """Test that extracted quota has all expected fields."""
    user = await create_test_user(db_session, "complete_quota")
    await db_session.commit()

    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    # Check all expected fields exist
    assert hasattr(extracted_quota, "id")
    assert hasattr(extracted_quota, "user_id")
    assert hasattr(extracted_quota, "free_quota_remaining")
    assert hasattr(extracted_quota, "next_reset")
    assert hasattr(extracted_quota, "created_at")
    assert hasattr(extracted_quota, "updated_at")

    # Check types
    assert isinstance(extracted_quota.id, int)
    assert isinstance(extracted_quota.user_id, int)
    assert isinstance(extracted_quota.free_quota_remaining, int)
    assert isinstance(extracted_quota.next_reset, datetime)
    assert extracted_quota.created_at is not None
    assert extracted_quota.updated_at is not None


@pytest.mark.asyncio
async def test_extract_quota_user_id_matches(db_session):
    """Test that extracted quota's user_id matches the requesting user."""
    user = await create_test_user(db_session, "matching_id")
    await db_session.commit()

    extracted_quota = await extract_free_user_quota_from_request(
        user=user, session=db_session
    )

    assert extracted_quota.user_id == user.id
