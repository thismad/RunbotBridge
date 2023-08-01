import argparse
from enum import Enum
from queue import Queue
import logging
from src.objects import CliMessage

logger = logging.getLogger(__name__)

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
        command = args.command.upper()
        if command == CliMessage.CliCommand.PAUSE.value:
            cli_message = CliMessage(CliMessage.CliCommand.PAUSE, None)
            q.put(cli_message)
            logger.info("Pausing script")
            print("Pausing script")

        elif command == CliMessage.CliCommand.RESUME.value:
            cli_message = CliMessage(CliMessage.CliCommand.RESUME, None)
            q.put(cli_message)
            logger.info("Resuming script")
            print("Resuming script")

        elif command == CliMessage.CliCommand.EXIT.value:
            cli_message = CliMessage(CliMessage.CliCommand.EXIT, None)
            q.put(cli_message)
            logger.info("Exiting script")
            print("Exiting script")
            break

