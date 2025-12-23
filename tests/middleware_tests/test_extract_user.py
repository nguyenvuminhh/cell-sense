"""
Tests for extract_user_from_request middleware.
"""

import pytest

from server.crud import users_crud
from server.middleware.extract_user_from_request import (
    extract_user_from_request,
)
from server.models.user_models import UserRequest


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
async def test_extract_user_existing_user(db_session):
    """Test extracting an existing user from the request."""
    # Create an existing user
    email = "existing_user@example.com"
    user_request = UserRequest(email=email, gemini_api_key="test_key_123")
    existing_user = await users_crud.create_user(db_session, user_request)
    await db_session.commit()

    # Extract the user
    extracted_user = await extract_user_from_request(
        user_email=email, session=db_session
    )

    assert extracted_user is not None
    assert extracted_user.email == email
    assert extracted_user.id == existing_user.id
    assert extracted_user.gemini_api_key == "test_key_123"


@pytest.mark.asyncio
async def test_extract_user_creates_new_user(db_session):
    """Test that a new user is created if they don't exist."""
    email = "new_user_middleware@example.com"

    # Verify user doesn't exist
    existing = await users_crud.get_user_with_email(db_session, email)
    assert existing is None

    # Extract user (should create new one)
    extracted_user = await extract_user_from_request(
        user_email=email, session=db_session
    )

    assert extracted_user is not None
    assert extracted_user.email == email
    assert extracted_user.gemini_api_key is None
    assert extracted_user.id is not None


@pytest.mark.asyncio
async def test_extract_user_creates_user_without_api_key(db_session):
    """Test that newly created user has no API key by default."""
    email = "no_api_key_user@example.com"

    extracted_user = await extract_user_from_request(
        user_email=email, session=db_session
    )

    assert extracted_user is not None
    assert extracted_user.email == email
    assert extracted_user.gemini_api_key is None


@pytest.mark.asyncio
async def test_extract_user_multiple_calls_same_email(db_session):
    """Test that multiple calls with same email return the same user."""
    email = "same_user@example.com"

    # First call - creates user
    user1 = await extract_user_from_request(
        user_email=email, session=db_session
    )
    await db_session.commit()

    # Second call - retrieves existing user
    user2 = await extract_user_from_request(
        user_email=email, session=db_session
    )

    assert user1.id == user2.id
    assert user1.email == user2.email


@pytest.mark.asyncio
async def test_extract_user_different_emails(db_session):
    """Test extracting different users with different emails."""
    email1 = "user1_diff@example.com"
    email2 = "user2_diff@example.com"

    user1 = await extract_user_from_request(
        user_email=email1, session=db_session
    )
    await db_session.commit()

    user2 = await extract_user_from_request(
        user_email=email2, session=db_session
    )
    await db_session.commit()

    assert user1.id != user2.id
    assert user1.email != user2.email
    assert user1.email == email1
    assert user2.email == email2


@pytest.mark.asyncio
async def test_extract_user_preserves_existing_api_key(db_session):
    """Test that extracting existing user preserves their API key."""
    email = "user_with_key@example.com"
    api_key = "important_api_key_123456"

    # Create user with API key
    user_request = UserRequest(email=email, gemini_api_key=api_key)
    await users_crud.create_user(db_session, user_request)
    await db_session.commit()

    # Extract user
    extracted_user = await extract_user_from_request(
        user_email=email, session=db_session
    )

    assert extracted_user.gemini_api_key == api_key


@pytest.mark.asyncio
async def test_extract_user_email_case_sensitive(db_session):
    """Test that email comparison is case-sensitive."""
    email_lower = "testuser@example.com"
    email_upper = "TESTUSER@example.com"

    user1 = await extract_user_from_request(
        user_email=email_lower, session=db_session
    )
    await db_session.commit()

    user2 = await extract_user_from_request(
        user_email=email_upper, session=db_session
    )
    await db_session.commit()

    # These should be different users
    assert user1.id != user2.id
    assert user1.email == email_lower
    assert user2.email == email_upper


@pytest.mark.asyncio
async def test_extract_user_with_special_characters_in_email(db_session):
    """Test extracting user with special characters in email."""
    email = "user+test@example.com"

    extracted_user = await extract_user_from_request(
        user_email=email, session=db_session
    )

    assert extracted_user is not None
    assert extracted_user.email == email


@pytest.mark.asyncio
async def test_extract_user_returns_complete_user_model(db_session):
    """Test that extracted user has all expected fields."""
    email = "complete_user@example.com"

    extracted_user = await extract_user_from_request(
        user_email=email, session=db_session
    )

    # Check all expected fields exist
    assert hasattr(extracted_user, "id")
    assert hasattr(extracted_user, "email")
    assert hasattr(extracted_user, "gemini_api_key")
    assert hasattr(extracted_user, "created_at")
    assert hasattr(extracted_user, "updated_at")

    # Check types
    assert isinstance(extracted_user.id, int)
    assert isinstance(extracted_user.email, str)
    assert extracted_user.created_at is not None
    assert extracted_user.updated_at is not None
