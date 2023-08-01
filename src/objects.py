from abc import ABC
from enum import Enum

class Message(ABC):
    def __init__(self, content):
        self.content = content
    pass

class WebhookMessage(Message):
    def __init__(self, content):
        super().__init__(content)

class CliMessage(Message):
    class CliCommand(Enum):
        PAUSE = 'PAUSE'
        RESUME = 'RESUME'
        EXIT = 'EXIT'

    def __init__(self, cli_command: CliCommand, content):
        super().__init__(content)
        self.command = cli_command

