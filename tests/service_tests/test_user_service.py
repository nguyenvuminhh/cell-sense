"""
Tests for user service functions.
"""

import pytest

from server.crud import users_crud
from server.models.user_models import ApiKeyUpdateRequest, UserRequest
from server.services import user_service


# Helper function to create a unique user for each test
async def create_test_user(
    session, email_suffix: str, api_key: str | None = None
):
    """Create a test user with unique email to avoid unique constraint violations."""
    user_request = UserRequest(
        email=f"test_{email_suffix}@example.com",
        gemini_api_key=api_key,
    )
    user = await users_crud.create_user(session, user_request)
    return user


@pytest.mark.asyncio
async def test_update_api_key_success(db_session):
    """Test successfully updating a user's API key."""
    # Create a user with an initial API key
    user = await create_test_user(
        db_session, "update_api_key", "old_api_key_123"
    )
    await db_session.commit()

    # Update the API key
    new_api_key = "new_api_key_456"
    update_request = ApiKeyUpdateRequest(gemini_api_key=new_api_key)

    updated_user = await user_service.update_api_key(
        db_session, update_request, user
    )

    assert updated_user is not None
    assert updated_user.gemini_api_key == new_api_key
    assert updated_user.email == user.email
    assert updated_user.id == user.id


@pytest.mark.asyncio
async def test_update_api_key_from_none(db_session):
    """Test updating API key when user previously had none."""
    # Create a user without an API key
    user = await create_test_user(db_session, "update_from_none", None)
    await db_session.commit()

    assert user.gemini_api_key is None

    # Add an API key
    new_api_key = "first_api_key_789"
    update_request = ApiKeyUpdateRequest(gemini_api_key=new_api_key)

    updated_user = await user_service.update_api_key(
        db_session, update_request, user
    )

    assert updated_user is not None
    assert updated_user.gemini_api_key == new_api_key


@pytest.mark.asyncio
async def test_update_api_key_to_empty_string(db_session):
    """Test updating API key to an empty string."""
    # Create a user with an API key
    user = await create_test_user(
        db_session, "update_to_empty", "existing_key_123"
    )
    await db_session.commit()

    # Update to empty string
    update_request = ApiKeyUpdateRequest(gemini_api_key="")

    updated_user = await user_service.update_api_key(
        db_session, update_request, user
    )

    assert updated_user is not None
    assert updated_user.gemini_api_key == ""


@pytest.mark.asyncio
async def test_update_api_key_multiple_times(db_session):
    """Test updating API key multiple times for the same user."""
    # Create a user
    user = await create_test_user(db_session, "update_multiple", "initial_key")
    await db_session.commit()

    # First update
    update_request_1 = ApiKeyUpdateRequest(gemini_api_key="second_key")
    updated_user_1 = await user_service.update_api_key(
        db_session, update_request_1, user
    )
    await db_session.commit()

    assert updated_user_1.gemini_api_key == "second_key"

    # Second update
    update_request_2 = ApiKeyUpdateRequest(gemini_api_key="third_key")
    updated_user_2 = await user_service.update_api_key(
        db_session, update_request_2, updated_user_1
    )
    await db_session.commit()

    assert updated_user_2.gemini_api_key == "third_key"
    assert updated_user_2.id == user.id


@pytest.mark.asyncio
async def test_update_api_key_preserves_other_fields(db_session):
    """Test that updating API key doesn't affect other user fields."""
    # Create a user
    original_email = "test_preserve_fields@example.com"
    user_request = UserRequest(
        email=original_email,
        gemini_api_key="original_key",
    )
    user = await users_crud.create_user(db_session, user_request)
    await db_session.commit()

    original_id = user.id
    original_created_at = user.created_at

    # Update API key
    update_request = ApiKeyUpdateRequest(gemini_api_key="new_key")
    updated_user = await user_service.update_api_key(
        db_session, update_request, user
    )

    # Verify other fields remain unchanged
    assert updated_user.id == original_id
    assert updated_user.email == original_email
    assert updated_user.created_at == original_created_at
    # updated_at might change, so we don't check it


@pytest.mark.asyncio
async def test_update_api_key_long_key(db_session):
    """Test updating with a very long API key."""
    user = await create_test_user(db_session, "long_key", None)
    await db_session.commit()

    # Create a long API key
    long_key = "a" * 100
    update_request = ApiKeyUpdateRequest(gemini_api_key=long_key)

    updated_user = await user_service.update_api_key(
        db_session, update_request, user
    )

    assert updated_user is not None
    assert updated_user.gemini_api_key == long_key
