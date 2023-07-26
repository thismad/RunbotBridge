from abc import ABC
from enum import Enum

class MessageType(Enum):
    """
    Enum for message types
    """
    WEBHOOK = 'WEBHOOK'
    CLI = 'CLI'


class Message(ABC):
    def __init__(self, type):
        self.type = type
    pass