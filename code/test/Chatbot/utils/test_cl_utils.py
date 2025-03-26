import unittest
from unittest.mock import AsyncMock, patch
from Chatbot.utils.cl_utils import send_message, send_animated_message
import asyncio


class TestCLUtils(unittest.IsolatedAsyncioTestCase):

    @patch("chainlit.Message.send", new_callable=AsyncMock)
    async def test_send_message_without_actions(self, mock_send):
        await send_message("Test message")
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0].content, "Test message")

    @patch("chainlit.Message.send", new_callable=AsyncMock)
    async def test_send_message_with_actions(self, mock_send):
        actions = [{"name": "Action1", "value": "Value1"}]
        await send_message("Test message with actions", actions=actions)
        mock_send.assert_called_once()
        self.assertEqual(
            mock_send.call_args[0][0].content, "Test message with actions")
        self.assertEqual(mock_send.call_args[0][0].actions, actions)

    @patch("chainlit.Message.update", new_callable=AsyncMock)
    @patch("chainlit.Message.send", new_callable=AsyncMock)
    async def test_send_animated_message(self, mock_send, mock_update):
        frames = ["Frame 1", "Frame 2", "Frame 3"]
        base_msg = "Loading"
        interval = 0.1
        timeout = 0.3

        async def run_animation():
            await send_animated_message(base_msg, frames, interval=interval, timeout=timeout)

        task = asyncio.create_task(run_animation())
        await asyncio.sleep(timeout + 0.1)  # Allow animation to complete
        task.cancel()

        mock_send.assert_called_once()
        self.assertTrue(mock_update.called)
        self.assertGreaterEqual(mock_update.call_count, len(frames))


if __name__ == "__main__":
    unittest.main()
