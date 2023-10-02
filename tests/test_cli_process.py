from unittest import TestCase
from unittest.mock import patch, Mock

from src.cli_process import cli_process
from src.objects import CliMessage, Message


class TestCli(TestCase):
    @patch('builtins.input', side_effect=['pause', 'resume', 'exit'])
    @patch('redis.Redis')
    def test_cli_process(self, mock_redis, mock_input):
        # Create a mock Redis instance
        mock_r = Mock()
        mock_redis.return_value = mock_r

        # Run the cli_process function
        cli_process(mock_r)

        # Check the calls to the mock Redis publish method (or whatever method you're using)
        # This example assumes you are using a method named publish
        calls = [Message.deserialize_message(call[0][1]) for call in mock_r.rpush.call_args_list]
        print(calls)

        # Validate the calls were as expected
        self.assertListEqual(calls,
                             [CliMessage(CliMessage.CliCommand.PAUSE),
                              CliMessage(CliMessage.CliCommand.RESUME),
                              CliMessage(CliMessage.CliCommand.EXIT)])
