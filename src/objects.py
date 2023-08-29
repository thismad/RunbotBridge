import json
from abc import ABC
from enum import Enum


class Message(ABC):
    """
    Abstract class for messages between processes
    """
    @staticmethod
    def deserialize_message(json_string: str):
        """
        Deserialize a message from a JSON string
        :param json_string:
        :return:
        """
        message = json.loads(json_string)
        if message['type'] == 'CliMessage':
            command = message['command'].upper()
            return CliMessage(CliMessage.CliCommand(command))
        elif message['type'] == 'WebhookMessage':
            return WebhookMessage(message['content'])


class WebhookMessage(Message):
    """
    Message sent by the webhook listener
    """
    def __init__(self, content):
        super().__init__()
        self.content = content

    def serialize_message(self):
        """
        Serialize the message to a JSON string
        :return:
        """
        return json.dumps({'type': 'WebhookMessage', 'content': self.content})

    def __repr__(self):
        return f"WebhookMessage({self.content}])"


class CliMessage(Message):
    """
    Message sent by the CLI process
    """
    class CliCommand(Enum):
        PAUSE = 'PAUSE'
        RESUME = 'RESUME'
        EXIT = 'EXIT'

    def __init__(self, cli_command: CliCommand):
        super().__init__()
        self.command = cli_command

    def serialize_message(self):
        """
        Serialize the message to a JSON string
        :return:
        """
        return json.dumps({'type': 'CliMessage', 'command': self.command.value})

    def __eq__(self, other):
        if isinstance(other, CliMessage):
            return self.command == other.command
        return False

    def __repr__(self):
        return f"CliMessage({self.command}])"
