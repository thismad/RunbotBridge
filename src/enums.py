from enum import Enum
class MessageType(Enum):
    """
    Enum for message types
    """
    WEBHOOK = 'WEBHOOK'
    CLI = 'CLI'