import argparse
from enum import Enum
from queue import Queue
import logging
from src.objects import Message

logger = logging.getLogger(__name__)

class CliMessage(Message):
    class CliCommand(Enum):
        PAUSE = 'pause'
        RESUME = 'resume'
        EXIT = 'exit'

    def __init__(self, type: CliCommand, content):
        super().__init__(type)
        self.content = content

def cli_process(q:Queue):
    parser = argparse.ArgumentParser(description='Key CLI manager for the bridge')

    # Define the arguments you expect
    parser.add_argument('command', type=str)

    while True:
        user_input = input("""Waiting for command:
        - pause : Pause the script
        - resume : Resume the script
        - exit : Close the bridge""")
        args = parser.parse_args(user_input.split(sep=" ", maxsplit=1))
        if args.command == 'pause':
            cli_message = CliMessage(CliMessage.CliCommand.PAUSE, None)
            q.put(cli_message)
            logger.info("Pausing script")
            print("Pausing script")

        if args.command == 'resume':
            cli_message = CliMessage(CliMessage.CliCommand.RESUME, None)
            q.put(cli_message)
            logger.info("Resuming script")
            print("Resuming script")

        if args.command == 'exit':
            cli_message = CliMessage(CliMessage.CliCommand.EXIT, None)
            q.put(cli_message)
            logger.info("Exiting script")
            print("Exiting script")
            break

