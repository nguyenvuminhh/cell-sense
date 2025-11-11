import pytest

from server.crud.users_crud import (
    _create_user,
    _delete_user,
    _get_user_with_email,
    _update_user,
)
from server.models.user_models import UserRequest


@pytest.mark.asyncio
async def test_create_user(db_session):
    user_req = UserRequest(email="john@example.com")
    user = await _create_user(db_session, user_req)
    assert user.email == "john@example.com"
    assert user.id is not None
    assert user.gemini_api_key is None


@pytest.mark.asyncio
async def test_get_user_with_email(db_session):
    user_req = UserRequest(email="alice@example.com")
    await _create_user(db_session, user_req)

    user = await _get_user_with_email(db_session, "alice@example.com")
    assert user is not None
    assert user.email == "alice@example.com"
    assert user.gemini_api_key is None


@pytest.mark.asyncio
async def test_update_user(db_session):
    user_req = UserRequest(email="bob@example.com")
    created_user = await _create_user(db_session, user_req)
    assert created_user.gemini_api_key is None

    update_req = UserRequest(
        email="bobby@example.com", gemini_api_key="SomeKey"
    )
    updated_user = await _update_user(db_session, created_user.id, update_req)
    assert updated_user is not None
    assert updated_user.email == "bobby@example.com"
    assert updated_user.gemini_api_key == "SomeKey"


@pytest.mark.asyncio
async def test_delete_user(db_session):
    user_req = UserRequest(email="eve@example.com")
    created_user = await _create_user(db_session, user_req)

    result = await _delete_user(db_session, created_user.id)
    assert result is True

    deleted_user = await _get_user_with_email(db_session, "eve@example.com")
    assert deleted_user is None

    result = await _delete_user(db_session, created_user.id)
    assert result is False
