import argparse
import logging

import redis

from .objects import CliMessage

log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)


def cli_process():
    r = redis.Redis(host='redis')
    parser = argparse.ArgumentParser(description='Key CLI manager for the bridge')

    # Define the arguments you expect
    parser.add_argument('command', type=str)
    paused = False
    while True:
        user_input = input(f"""Waiting for command:
        - pause : Pause the script
        - resume : Resume the script
        - exit : Close the bridge\n
        Status : {'Paused' if paused else 'Running'}\n""")
        args = parser.parse_args(user_input.split(sep=" ", maxsplit=1))
        command = args.command.upper()
        if command == CliMessage.CliCommand.PAUSE.value:
            cli_message = CliMessage(CliMessage.CliCommand.PAUSE)
            r.rpush("communication", cli_message.serialize_message())
            paused = True
            logger.info("Pausing script")

        elif command == CliMessage.CliCommand.RESUME.value:
            cli_message = CliMessage(CliMessage.CliCommand.RESUME)
            r.rpush("communication", cli_message.serialize_message())
            paused = False
            logger.info("Resuming script")

        elif command == CliMessage.CliCommand.EXIT.value:
            cli_message = CliMessage(CliMessage.CliCommand.EXIT)
            r.rpush("communication", cli_message.serialize_message())
            logger.info("Exiting script")
            break


if __name__ == '__main__':
    logger.info("Starting CLI")
    cli_process()
