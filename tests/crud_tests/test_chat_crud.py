import pytest

from server.constants import LLMModels
from server.crud.chats_crud import (
    _create_chat,
    _create_message,
    _delete_chat,
    _delete_message,
    _get_chat,
    _get_chats_by_user,
    _get_messages_by_chat,
    _update_chat,
)
from server.crud.users_crud import _create_user
from server.models.chat_models import ChatMessageRequest
from server.models.user_models import UserRequest


@pytest.mark.asyncio
async def test_create_chat(db_session):
    # Create a user first
    user_req = UserRequest(email="chatuser@example.com")
    user = await _create_user(db_session, user_req)

    # Create a chat
    chat = await _create_chat(db_session, user.id)

    assert chat.title == "My First Chat"
    assert chat.user_id == user.id
    assert chat.id is not None
    assert chat.created_at is not None
    assert chat.updated_at is not None


@pytest.mark.asyncio
async def test_create_chat_with_default_title(db_session):
    # Create a user first
    user_req = UserRequest(email="defaultuser@example.com")
    user = await _create_user(db_session, user_req)

    # Create a chat with default title
    chat = await _create_chat(db_session, user.id)

    assert chat.title == "New Chat"
    assert chat.user_id == user.id


@pytest.mark.asyncio
async def test_get_chat(db_session):
    # Create a user and chat
    user_req = UserRequest(email="getuser@example.com")
    user = await _create_user(db_session, user_req)

    created_chat = await _create_chat(db_session, user.id)

    # Get the chat
    chat = await _get_chat(db_session, created_chat.id)
    assert chat is not None
    assert chat.id == created_chat.id
    assert chat.title == "Get Chat Test"
    assert chat.user_id == user.id


@pytest.mark.asyncio
async def test_update_chat_title(db_session):
    # Create a user and chat
    user_req = UserRequest(email="updateuser@example.com")
    user = await _create_user(db_session, user_req)

    created_chat = await _create_chat(db_session, user.id)

    # Update the chat title
    new_title = "Updated Chat Title"
    updated_chat = await _update_chat(db_session, created_chat.id, new_title)
    assert updated_chat is not None
    assert updated_chat.title == new_title
    assert updated_chat.id == created_chat.id
    assert updated_chat.user_id == user.id


@pytest.mark.asyncio
async def test_get_chat_not_found(db_session):
    # Try to get non-existent chat
    chat = await _get_chat(db_session, 99999)
    assert chat is None


@pytest.mark.asyncio
async def test_get_chats_by_user(db_session):
    # Create a user
    user_req = UserRequest(email="multiuser@example.com")
    user = await _create_user(db_session, user_req)

    # Create multiple chats
    chat1 = await _create_chat(db_session, user.id)

    chat2 = await _create_chat(db_session, user.id)

    chat3 = await _create_chat(db_session, user.id)

    # Get all chats for user
    chats = await _get_chats_by_user(db_session, user.id)
    assert len(chats) == 3
    # Should be ordered by updated_at desc
    assert (
        chats[0].id == chat3.id
    ), f"Expected chat3.id {chat3.id}, got {chats[0].id}. Other ids: {[f'Chat {chat.id} at {chat.updated_at}' for chat in chats]}"
    assert (
        chats[1].id == chat2.id
    ), f"Expected chat2.id {chat2.id}, got {chats[1].id}. Other ids: {[f'Chat {chat.id} at {chat.updated_at}' for chat in chats]}"
    assert (
        chats[2].id == chat1.id
    ), f"Expected chat1.id {chat1.id}, got {chats[2].id}. Other ids: {[f'Chat {chat.id} at {chat.updated_at}' for chat in chats]}"


@pytest.mark.asyncio
async def test_get_chats_by_user_empty(db_session):
    # Create a user with no chats
    user_req = UserRequest(email="emptyuser@example.com")
    user = await _create_user(db_session, user_req)

    # Get chats
    chats = await _get_chats_by_user(db_session, user.id)
    assert len(chats) == 0


@pytest.mark.asyncio
async def test_delete_chat(db_session):
    # Create a user and chat
    user_req = UserRequest(email="deleteuser@example.com")
    user = await _create_user(db_session, user_req)

    created_chat = await _create_chat(db_session, user.id)

    # Delete the chat
    result = await _delete_chat(db_session, created_chat.id)
    assert result is True

    # Verify it's deleted
    deleted_chat = await _get_chat(db_session, created_chat.id)
    assert deleted_chat is None


@pytest.mark.asyncio
async def test_delete_chat_not_found(db_session):
    # Try to delete non-existent chat
    result = await _delete_chat(db_session, 99999)
    assert result is False


@pytest.mark.asyncio
async def test_create_message_from_user(db_session):
    # Create a user and chat
    user_req = UserRequest(email="msguser@example.com")
    user = await _create_user(db_session, user_req)

    chat = await _create_chat(db_session, user.id)

    # Create a message from user
    message_req = ChatMessageRequest(
        chat_id=chat.id,
        content="Hello from user",
        is_from_user=True,
        model_name=None,
    )
    message = await _create_message(db_session, message_req)

    assert message.chat_id == chat.id
    assert message.content == "Hello from user"
    assert message.is_from_user is True
    assert message.model_name is None
    assert message.id is not None
    assert message.created_at is not None


@pytest.mark.asyncio
async def test_create_message_from_llm(db_session):
    # Create a user and chat
    user_req = UserRequest(email="llmuser@example.com")
    user = await _create_user(db_session, user_req)

    chat = await _create_chat(db_session, user.id)

    # Create a message from LLM
    message_req = ChatMessageRequest(
        chat_id=chat.id,
        content="Hello from LLM",
        is_from_user=False,
        model_name=LLMModels.GOOGLE_GEMINI_2_5_FLASH,
    )
    message = await _create_message(db_session, message_req)

    assert message.chat_id == chat.id
    assert message.content == "Hello from LLM"
    assert message.is_from_user is False
    assert message.model_name == LLMModels.GOOGLE_GEMINI_2_5_FLASH


@pytest.mark.asyncio
async def test_create_message_from_llm_without_model_name(db_session):
    # Create a user and chat
    user_req = UserRequest(email="llmnomodel@example.com")
    user = await _create_user(db_session, user_req)

    chat = await _create_chat(db_session, user.id)

    # Try to create a message from LLM without model_name
    with pytest.raises(ValueError, match="model_name must be provided"):
        ChatMessageRequest(
            chat_id=chat.id,
            content="Hello from LLM",
            is_from_user=False,
            model_name=None,
        )


@pytest.mark.asyncio
async def test_get_messages_by_chat(db_session):
    # Create a user and chat
    user_req = UserRequest(email="msglistuser@example.com")
    user = await _create_user(db_session, user_req)

    chat = await _create_chat(db_session, user.id)

    # Create multiple messages
    msg1_req = ChatMessageRequest(
        chat_id=chat.id,
        content="First message",
        is_from_user=True,
    )
    msg1 = await _create_message(db_session, msg1_req)

    msg2_req = ChatMessageRequest(
        chat_id=chat.id,
        content="Second message",
        is_from_user=False,
        model_name=LLMModels.GOOGLE_GEMINI_2_5_FLASH,
    )
    msg2 = await _create_message(db_session, msg2_req)

    msg3_req = ChatMessageRequest(
        chat_id=chat.id,
        content="Third message",
        is_from_user=True,
    )
    msg3 = await _create_message(db_session, msg3_req)

    # Get all messages for chat
    messages = await _get_messages_by_chat(db_session, chat.id)
    assert len(messages) == 3
    # Should be ordered by created_at asc
    assert messages[0].id == msg1.id
    assert messages[0].content == "First message"
    assert messages[1].id == msg2.id
    assert messages[1].content == "Second message"
    assert messages[2].id == msg3.id
    assert messages[2].content == "Third message"


@pytest.mark.asyncio
async def test_get_messages_by_chat_empty(db_session):
    # Create a user and chat
    user_req = UserRequest(email="emptymsguser@example.com")
    user = await _create_user(db_session, user_req)

    chat = await _create_chat(db_session, user.id)

    # Get messages for empty chat
    messages = await _get_messages_by_chat(db_session, chat.id)
    assert len(messages) == 0


@pytest.mark.asyncio
async def test_delete_message(db_session):
    # Create a user and chat
    user_req = UserRequest(email="delmsguser@example.com")
    user = await _create_user(db_session, user_req)

    chat = await _create_chat(db_session, user.id)

    # Create a message
    message_req = ChatMessageRequest(
        chat_id=chat.id,
        content="To be deleted",
        is_from_user=True,
    )
    message = await _create_message(db_session, message_req)

    # Delete the message
    result = await _delete_message(db_session, message.id)
    assert result is True

    # Verify it's deleted
    messages = await _get_messages_by_chat(db_session, chat.id)
    assert len(messages) == 0


@pytest.mark.asyncio
async def test_delete_message_not_found(db_session):
    # Try to delete non-existent message
    result = await _delete_message(db_session, 99999)
    assert result is False


@pytest.mark.asyncio
async def test_chat_isolation_between_users(db_session):
    # Create two users
    user1_req = UserRequest(email="user1@example.com")
    user1 = await _create_user(db_session, user1_req)

    user2_req = UserRequest(email="user2@example.com")
    user2 = await _create_user(db_session, user2_req)

    # Create chats for each user
    await _create_chat(db_session, user1.id)
    await _create_chat(db_session, user2.id)

    # Verify each user only sees their own chats
    user1_chats = await _get_chats_by_user(db_session, user1.id)
    user2_chats = await _get_chats_by_user(db_session, user2.id)

    assert len(user1_chats) == 1
    assert len(user2_chats) == 1
    assert user1_chats[0].title == "User1 Chat"
    assert user2_chats[0].title == "User2 Chat"
