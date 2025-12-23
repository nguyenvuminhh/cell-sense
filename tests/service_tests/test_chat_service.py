"""
Tests for chat service functions.
"""

from datetime import datetime, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from server.constants import DEFAULT_CHAT_NAME, LLMModels, LLMProviders
from server.crud import free_user_quota_crud, users_crud
from server.middleware import NotFoundError
from server.models.chat_models import ChatMessageRequest
from server.models.exception_models import BadRequestError, ForbiddenError
from server.models.free_user_quota_models import FreeUserQuotaRequest
from server.models.message_models import MessageRequest, SelectedRange
from server.models.user_models import UserRequest
from server.services import chat_service


# Helper function to create a unique user for each test
async def create_test_user(session, email_suffix: str):
    """Create a test user with unique email to avoid unique constraint violations."""
    user_request = UserRequest(
        email=f"test_{email_suffix}@example.com",
        gemini_api_key="test_api_key_1234567890",
    )
    user = await users_crud.create_user(session, user_request)
    return user


@pytest.mark.asyncio
async def test_create_chat(db_session):
    """Test creating a new chat for a user."""
    # Create a unique user for this test
    user = await create_test_user(db_session, "create_chat")

    # Create a chat
    chat = await chat_service.create_chat(db_session, user)

    assert chat is not None
    assert chat.user_id == user.id
    assert chat.title == DEFAULT_CHAT_NAME
    assert chat.messages == []


@pytest.mark.asyncio
async def test_get_latest_chat_creates_new_if_none_exist(db_session):
    """Test get_latest_chat creates a new chat if user has no chats."""
    user = await create_test_user(db_session, "latest_chat_new")

    # Get latest chat (should create a new one)
    chat = await chat_service.get_latest_chat(db_session, user)

    assert chat is not None
    assert chat.user_id == user.id
    assert chat.title == DEFAULT_CHAT_NAME


@pytest.mark.asyncio
async def test_get_latest_chat_returns_most_recent(db_session):
    """Test get_latest_chat returns the most recently updated chat."""
    user = await create_test_user(db_session, "latest_chat_recent")

    # Create multiple chats
    await chat_service.create_chat(db_session, user)
    chat2 = await chat_service.create_chat(db_session, user)
    await db_session.commit()

    # Get latest chat (should be chat2 as it was created most recently)
    latest_chat = await chat_service.get_latest_chat(db_session, user)

    assert latest_chat is not None
    assert latest_chat.id == chat2.id


@pytest.mark.asyncio
async def test_get_chat_success(db_session):
    """Test successfully retrieving a chat by ID."""
    user = await create_test_user(db_session, "get_chat_success")
    chat = await chat_service.create_chat(db_session, user)
    await db_session.commit()

    # Get the chat
    retrieved_chat = await chat_service.get_chat(db_session, chat.id, user)

    assert retrieved_chat is not None
    assert retrieved_chat.id == chat.id
    assert retrieved_chat.user_id == user.id


@pytest.mark.asyncio
async def test_get_chat_not_found(db_session):
    """Test getting a chat that doesn't exist raises NotFoundError."""
    user = await create_test_user(db_session, "get_chat_not_found")

    # Try to get a non-existent chat
    with pytest.raises(NotFoundError) as exc_info:
        await chat_service.get_chat(db_session, 99999, user)

    assert "not found" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_chat_access_denied(db_session):
    """Test getting a chat owned by another user raises HTTPException."""
    user1 = await create_test_user(db_session, "get_chat_user1")
    user2 = await create_test_user(db_session, "get_chat_user2")

    # Create chat for user1
    chat = await chat_service.create_chat(db_session, user1)
    await db_session.commit()

    # Try to access with user2
    with pytest.raises(ForbiddenError) as exc_info:
        await chat_service.get_chat(db_session, chat.id, user2)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_chat_success(db_session):
    """Test successfully deleting a chat."""
    user = await create_test_user(db_session, "delete_chat_success")
    chat = await chat_service.create_chat(db_session, user)
    await db_session.commit()

    # Delete the chat
    result = await chat_service.delete_chat(db_session, chat.id, user)

    assert result is True

    # Verify chat was deleted
    with pytest.raises(NotFoundError):
        await chat_service.get_chat(db_session, chat.id, user)


@pytest.mark.asyncio
async def test_delete_chat_not_found(db_session):
    """Test deleting a non-existent chat raises NotFoundError."""
    user = await create_test_user(db_session, "delete_chat_not_found")

    with pytest.raises(NotFoundError):
        await chat_service.delete_chat(db_session, 99999, user)


@pytest.mark.asyncio
async def test_delete_chat_access_denied(db_session):
    """Test deleting a chat owned by another user raises HTTPException."""
    user1 = await create_test_user(db_session, "delete_chat_user1")
    user2 = await create_test_user(db_session, "delete_chat_user2")

    chat = await chat_service.create_chat(db_session, user1)
    await db_session.commit()

    with pytest.raises(ForbiddenError) as exc_info:
        await chat_service.delete_chat(db_session, chat.id, user2)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_user_chats(db_session):
    """Test getting all chats for a user."""
    user = await create_test_user(db_session, "get_user_chats")

    # Create chats with messages
    chat1 = await chat_service.create_chat(db_session, user)
    await chat_service.create_chat(db_session, user)

    # Add messages to chat1
    message_request = ChatMessageRequest(
        chat_id=chat1.id,
        content="Test message",
        is_from_user=True,
        full_user_prompt="Full prompt",
    )
    await chat_service.create_message(
        db_session, chat1.id, user, message_request
    )
    await db_session.commit()

    # Get user chats (should only return chat1 as chat2 has no messages)
    chats = await chat_service.get_user_chats(user, db_session)

    assert len(chats) == 1
    assert chats[0].id == chat1.id
    assert len(chats[0].messages) > 0


@pytest.mark.asyncio
async def test_get_user_chats_filters_empty_chats(db_session):
    """Test that get_user_chats filters out and deletes chats with no messages."""
    user = await create_test_user(db_session, "filter_empty_chats")

    # Create an empty chat
    await chat_service.create_chat(db_session, user)
    await db_session.commit()

    # Get user chats
    chats = await chat_service.get_user_chats(user, db_session)

    # Should return empty list as the chat has no messages
    assert len(chats) == 0


@pytest.mark.asyncio
async def test_get_chat_messages(db_session):
    """Test getting all messages for a chat."""
    user = await create_test_user(db_session, "get_chat_messages")
    chat = await chat_service.create_chat(db_session, user)

    # Create messages
    message1 = ChatMessageRequest(
        chat_id=chat.id,
        content="First message",
        is_from_user=True,
        full_user_prompt="Full prompt 1",
    )
    message2 = ChatMessageRequest(
        chat_id=chat.id,
        content="Second message",
        is_from_user=False,
        model_name=LLMModels.GOOGLE_GEMINI_2_5_FLASH_LITE,
        full_model_response='{"message": "response"}',
    )

    await chat_service.create_message(db_session, chat.id, user, message1)
    await chat_service.create_message(db_session, chat.id, user, message2)
    await db_session.commit()

    # Get messages
    messages = await chat_service.get_chat_messages(db_session, chat.id, user)

    assert len(messages) == 2
    assert messages[0].content == "First message"
    assert messages[1].content == "Second message"


@pytest.mark.asyncio
async def test_get_chat_messages_access_denied(db_session, monkeypatch):
    """Test getting messages for a chat owned by another user raises HTTPException."""

    user1 = await create_test_user(db_session, "messages_user1")
    user2 = await create_test_user(db_session, "messages_user2")

    chat = await chat_service.create_chat(db_session, user1)
    await db_session.commit()

    with pytest.raises(ForbiddenError) as exc_info:
        await chat_service.get_chat_messages(db_session, chat.id, user2)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_create_message_success(db_session):
    """Test successfully creating a message."""
    user = await create_test_user(db_session, "create_message")
    chat = await chat_service.create_chat(db_session, user)

    message_request = ChatMessageRequest(
        chat_id=chat.id,
        content="Test message",
        is_from_user=True,
        full_user_prompt="Full prompt",
    )

    message = await chat_service.create_message(
        db_session, chat.id, user, message_request
    )

    assert message is not None
    assert message.chat_id == chat.id
    assert message.content == "Test message"
    assert message.is_from_user is True


@pytest.mark.asyncio
async def test_create_message_chat_id_mismatch(db_session):
    """Test creating a message with mismatched chat_id in URL and body raises HTTPException."""
    user = await create_test_user(db_session, "message_mismatch")
    chat = await chat_service.create_chat(db_session, user)

    # Create message request with different chat_id
    message_request = ChatMessageRequest(
        chat_id=chat.id + 1,
        content="Test message",
        is_from_user=True,
        full_user_prompt="Full prompt",
    )

    with pytest.raises(HTTPException) as exc_info:
        await chat_service.create_message(
            db_session, chat.id, user, message_request
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_delete_message_success(db_session):
    """Test successfully deleting a message."""
    user = await create_test_user(db_session, "delete_message")
    chat = await chat_service.create_chat(db_session, user)

    message_request = ChatMessageRequest(
        chat_id=chat.id,
        content="Test message",
        is_from_user=True,
        full_user_prompt="Full prompt",
    )

    message = await chat_service.create_message(
        db_session, chat.id, user, message_request
    )
    await db_session.commit()

    # Delete the message
    result = await chat_service.delete_message(db_session, message.id)

    assert result is True


@pytest.mark.asyncio
async def test_delete_message_not_found(db_session):
    """Test deleting a non-existent message raises NotFoundError."""
    with pytest.raises(NotFoundError):
        await chat_service.delete_message(db_session, 99999)


@pytest.mark.asyncio
async def test_handle_message_with_user_api_key(db_session):
    """Test handle_message with user-provided API key."""
    user = await create_test_user(db_session, "handle_message_user_key")
    chat = await chat_service.create_chat(db_session, user)
    await free_user_quota_crud.create_free_user_quota(
        db_session,
        FreeUserQuotaRequest(
            user_id=user.id,
            free_quota_remaining=10,
            next_reset=datetime.combine(datetime.today(), time(23, 59, 59)),
        ),
    )

    await db_session.commit()

    # Create a message request
    message_request = MessageRequest(
        message="Test question",
        selected_ranges=[
            SelectedRange(
                sheet_name_and_range="Sheet1!A1:B2",
                cell_values=[["A", "B"], ["C", "D"]],
            )
        ],
        llm_provider=LLMProviders.GOOGLE,
        llm_model=LLMModels.GOOGLE_GEMINI_2_5_FLASH_LITE,
    )

    # Mock the LLM service and API key
    with (
        patch(
            "server.services.llm_service.generate_response",
            new_callable=AsyncMock,
        ) as mock_llm,
        patch("server.services.chat_service.GEMINI_API_KEY", "mock_system_key"),
    ):

        # Set up side_effect to return different responses based on template_name
        def create_mock_response(*args, **kwargs):
            template_name = kwargs.get("template_name")
            # Check if it's the title naming template
            if template_name and str(template_name).endswith(
                "llm_title_naming_prompt.md"
            ):
                mock_resp = MagicMock()
                mock_resp.full_user_prompt = "Title prompt"
                mock_resp.full_model_response = (
                    '{"title": "Test Chat Title", "message_is_unclear": false}'
                )
                return mock_resp
            else:
                mock_resp = MagicMock()
                mock_resp.full_user_prompt = "Full user prompt"
                mock_resp.full_model_response = (
                    '{"message": "Test response", "filled_ranges": []}'
                )
                return mock_resp

        mock_llm.side_effect = create_mock_response

        response = await chat_service.handle_message(
            db_session, message_request, user, chat.id
        )

        assert response is not None
        assert response.message == "Test response"
        assert mock_llm.called


@pytest.mark.asyncio
async def test_handle_message_uses_free_quota(db_session):
    """Test handle_message uses free quota when user has no API key."""
    # Create user without API key
    user_request = UserRequest(
        email="test_free_quota@example.com",
        gemini_api_key=None,
    )
    user = await users_crud.create_user(db_session, user_request)

    # Create free quota for user
    from server.crud import free_user_quota_crud

    quota_request = FreeUserQuotaRequest(
        user_id=user.id,
        free_quota_remaining=10,
        next_reset=datetime.combine(datetime.today(), time(23, 59, 59)),
    )
    await free_user_quota_crud.create_free_user_quota(db_session, quota_request)

    chat = await chat_service.create_chat(db_session, user)
    await db_session.commit()

    message_request = MessageRequest(
        message="Test question",
        selected_ranges=[
            SelectedRange(
                sheet_name_and_range="Sheet1!A1:B2",
                cell_values=[["A", "B"], ["C", "D"]],
            )
        ],
    )

    # Mock both LLM service and system API key
    with (
        patch(
            "server.services.llm_service.generate_response",
            new_callable=AsyncMock,
        ) as mock_llm,
        patch("server.services.chat_service.GEMINI_API_KEY", "system_api_key"),
    ):

        # Set up side_effect to return different responses based on template_name
        def create_mock_response(*args, **kwargs):
            template_name = kwargs.get("template_name")
            # Check if it's the title naming template
            if template_name and str(template_name).endswith(
                "llm_title_naming_prompt.md"
            ):
                mock_resp = MagicMock()
                mock_resp.full_user_prompt = "Title prompt"
                mock_resp.full_model_response = (
                    '{"title": "Test Chat Title", "message_is_unclear": false}'
                )
                return mock_resp
            else:
                mock_resp = MagicMock()
                mock_resp.full_user_prompt = "Full user prompt"
                mock_resp.full_model_response = (
                    '{"message": "Test response", "filled_ranges": []}'
                )
                return mock_resp

        mock_llm.side_effect = create_mock_response

        response = await chat_service.handle_message(
            db_session, message_request, user, chat.id
        )

        assert response is not None
        assert mock_llm.called


@pytest.mark.asyncio
async def test_handle_message_no_quota_left(db_session):
    """Test handle_message raises BadRequestError when user has no quota left."""
    # Create user without API key
    user_request = UserRequest(
        email="test_no_quota@example.com",
        gemini_api_key=None,
    )
    user = await users_crud.create_user(db_session, user_request)

    # Create free quota with 0 remaining
    from server.crud import free_user_quota_crud

    quota_request = FreeUserQuotaRequest(
        user_id=user.id,
        free_quota_remaining=0,
        next_reset=datetime.combine(datetime.today(), time(23, 59, 59)),
    )
    await free_user_quota_crud.create_free_user_quota(db_session, quota_request)

    chat = await chat_service.create_chat(db_session, user)
    await db_session.commit()

    message_request = MessageRequest(
        message="Test question",
        selected_ranges=[
            SelectedRange(
                sheet_name_and_range="Sheet1!A1:B2",
                cell_values=[["A", "B"], ["C", "D"]],
            )
        ],
    )

    with (
        patch(
            "server.services.llm_service.generate_response",
            new_callable=AsyncMock,
        ) as mock_llm,
        patch("server.services.chat_service.GEMINI_API_KEY", "system_api_key"),
    ):

        mock_resp = MagicMock()
        mock_resp.full_user_prompt = "Title prompt"
        mock_resp.full_model_response = (
            '{"title": "Test Chat Title", "message_is_unclear": false}'
        )
        mock_llm.return_value = mock_resp

        with pytest.raises(BadRequestError) as exc_info:
            await chat_service.handle_message(
                db_session, message_request, user, chat.id
            )

        assert "quota" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_handle_message_updates_chat_title(db_session):
    """Test handle_message updates chat title from default name."""
    user = await create_test_user(db_session, "update_title")
    chat = await chat_service.create_chat(db_session, user)
    await free_user_quota_crud.create_free_user_quota(
        db_session,
        FreeUserQuotaRequest(
            user_id=user.id,
            free_quota_remaining=10,
            next_reset=datetime.combine(datetime.today(), time(23, 59, 59)),
        ),
    )

    await db_session.commit()

    # Verify initial title is default
    assert chat.title == DEFAULT_CHAT_NAME

    message_request = MessageRequest(
        message="Test question",
        selected_ranges=[
            SelectedRange(
                sheet_name_and_range="Sheet1!A1:B2",
                cell_values=[["A", "B"], ["C", "D"]],
            )
        ],
    )

    # Mock both LLM service calls (for message and title)
    with (
        patch(
            "server.services.llm_service.generate_response",
            new_callable=AsyncMock,
        ) as mock_llm,
        patch("server.services.chat_service.GEMINI_API_KEY", "system_api_key"),
    ):

        # Set up side_effect to return different responses based on template_name
        def create_mock_response(*args, **kwargs):
            template_name = kwargs.get("template_name")
            # Check if it's the title naming template
            if template_name and str(template_name).endswith(
                "llm_title_naming_prompt.md"
            ):
                mock_resp = MagicMock()
                mock_resp.full_user_prompt = "Title prompt"
                mock_resp.full_model_response = (
                    '{"title": "New Chat Title", "message_is_unclear": false}'
                )
                return mock_resp
            else:
                mock_resp = MagicMock()
                mock_resp.full_user_prompt = "Full user prompt"
                mock_resp.full_model_response = (
                    '{"message": "Test response", "filled_ranges": []}'
                )
                return mock_resp

        mock_llm.side_effect = create_mock_response

        response = await chat_service.handle_message(
            db_session, message_request, user, chat.id
        )

        assert response is not None
        # Verify title was updated
        assert mock_llm.call_count == 2


@pytest.mark.asyncio
async def test_handle_message_chat_not_found(db_session):
    """Test handle_message raises NotFoundError for non-existent chat."""
    user = await create_test_user(db_session, "message_chat_not_found")

    message_request = MessageRequest(
        message="Test question",
        selected_ranges=[
            SelectedRange(
                sheet_name_and_range="Sheet1!A1:B2",
                cell_values=[["A", "B"], ["C", "D"]],
            )
        ],
    )

    with pytest.raises(NotFoundError):
        await chat_service.handle_message(
            db_session, message_request, user, 99999
        )
