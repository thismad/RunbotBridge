import queue
import argparse
import threading
from enum import Enum
from src.cli import cli_process, CliMessage

from objects import MessageType




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



