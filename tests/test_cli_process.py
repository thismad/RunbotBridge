import json
from queue import Queue
import threading
import unittest
import os
from unittest.mock import patch, MagicMock
from src.cli_process import cli_process
from src.objects import CliMessage

class TestCli(unittest.TestCase):
    @patch('builtins.input', side_effect=['pause', 'resume', 'exit'])
    @patch.object(Queue, 'put')
    def test_cli_process(self, mock_put, mock_input):
        q = Queue()
        cli_process()
        # check the call args of the mock_put
        calls = [call[0][0] for call in mock_put.call_args_list]
        commands = [call.command for call in calls]

        self.assertListEqual(commands,
                             [CliMessage.CliCommand.PAUSE, CliMessage.CliCommand.RESUME, CliMessage.CliCommand.EXIT])


