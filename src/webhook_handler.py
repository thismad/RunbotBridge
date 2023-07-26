from src.objects import Message
from src.objects import MessageType

class WebhookMessage(Message):
    def __init__(self, content):
        super().__init__(MessageType.WEBHOOK)
        self.content = content

