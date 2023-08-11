import logging
import queue
import threading

from .cli_process import cli_process
from .objects import WebhookMessage, CliMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Create a FIFO queue
    q = queue.Queue()

    # Create and start worker threads
    t1 = threading.Thread(target=cli_process, args=(q,))
    t1.start()
    while True:
        next_message = q.get()
        if isinstance(next_message, WebhookMessage):
            print('Webhook message')
            q.task_done()
        elif isinstance(next_message, CliMessage):
            print("Cli message :", next_message.content)
            q.task_done()
