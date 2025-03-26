import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import chainlit as cl
from Chatbot.app import on_chat_start, on_message, auth_callback


class TestApp(unittest.IsolatedAsyncioTestCase):

    @patch("Chatbot.app.cl.context.emitter.set_commands", new_callable=AsyncMock)
    @patch("Chatbot.app.cl.user_session.get")
    @patch("Chatbot.app.cl.Message.send", new_callable=AsyncMock)
    async def test_on_chat_start(self, mock_send, mock_user_session_get, mock_set_commands):
        mock_user_session_get.side_effect = lambda key: {
            "user": {"identifier": "test_user"}, "chat_profile": "Admin"}.get(key)
        await on_chat_start()
        mock_set_commands.assert_called_once()
        mock_send.assert_called_with(
            "👋 Welcome to the Transaction Admin System. How can I help you today?")

    @patch("Chatbot.app.cl.Message.send", new_callable=AsyncMock)
    async def test_auth_callback_success(self, mock_send):
        user = auth_callback("test_user", "wftest_user")
        self.assertIsNotNone(user)
        self.assertEqual(user.identifier, "test_user")

    @patch("Chatbot.app.cl.Message.send", new_callable=AsyncMock)
    async def test_auth_callback_failure(self, mock_send):
        user = auth_callback("test_user", "wrong_password")
        self.assertIsNone(user)

    @patch("Chatbot.app.cl.Message.send", new_callable=AsyncMock)
    @patch("Chatbot.app.cl.user_session.get")
    async def test_on_message_rules_command(self, mock_user_session_get, mock_send):
        mock_user_session_get.side_effect = lambda key: {
            "chat_profile": "Admin"}.get(key)
        mock_os_listdir = MagicMock(return_value=["rule1.json", "rule2.json"])
        with patch("os.listdir", mock_os_listdir):
            message = cl.Message(content="Rules rule1", command="Rules")
            await on_message(message)
            mock_send.assert_called()

    @patch("Chatbot.app.cl.Message.send", new_callable=AsyncMock)
    async def test_on_message_invalid_command(self, mock_send):
        message = cl.Message(content="Invalid command")
        await on_message(message)
        mock_send.assert_called_with("No response received")


if __name__ == "__main__":
    unittest.main()
