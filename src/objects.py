import json
from abc import ABC, abstractmethod
from enum import Enum


class Message(ABC):
    def __init__(self, content):
        self.content = content

    pass

    @abstractmethod
    def serialize_message(self):
        pass

    @staticmethod
    def deserialize_message(json_string):
        data = json.loads(json_string)

        if data['type'] == 'WebhookMessage':
            return WebhookMessage(data['content'])
        elif data['type'] == 'CliMessage':
            return CliMessage(CliMessage.CliCommand(data['command']), data['content'])
        else:
            raise Exception(f"Can't deserialize {data['type']}")


class WebhookMessage(Message):
    def __init__(self, content):
        super().__init__(content)

    def serialize_message(self):
        return json.dumps({'type': 'WebhookMessage', 'content': self.content})


class CliMessage(Message):
    class CliCommand(Enum):
        PAUSE = 'PAUSE'
        RESUME = 'RESUME'
        EXIT = 'EXIT'

    def __init__(self, cli_command: CliCommand, content):
        super().__init__(content)
        self.command = cli_command

    def serialize_message(self):
        return json.dumps({'type': 'CliMessage', 'command': self.command.value, 'content': self.content})
