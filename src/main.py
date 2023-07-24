import queue
import argparse
from enum import Enum

from enums import MessageType


class Message:
    def __init__(self, type):
        self.type = type

    pass


class WebhookMessage(Message):
    def __init__(self, content):
        self.content = content


class CliMessage(Message):
    class CliCommand(Enum):
        ADD = 'add'
        REMOVE = 'remove'
        PAUSE = 'pause'
        RESUME = 'resume'

    def __init__(self, type: CliCommand, content):
        super().__init__(type)
        self.content = content


def cli_process():
    parser = argparse.ArgumentParser(description='Key CLI manager for the bridge')

    # Define the arguments you expect
    parser.add_argument('command', type=str)
    parser.add_argument('parameters', type=str)

    while True:
        user_input = input("""Waiting for command:
        - add api_key secret_key passphrase pseudo: Add a key
        - remove api_key: Remove a key}""")
        args = parser.parse_args(user_input.split(sep=" ", maxsplit=1))
        if args.command == 'add':
            params = [param.strip() for param in args.parameters.split(' ')]
            if len(params) != 4:
                print("Invalid parameters. Expected format: api_key, secret_key, passphrase, pseudo")
                continue
            api_key, secret_key, passphrase, pseudo = params
            cli_message = CliMessage(CliMessage.CliCommand.ADD,
                                     {'api_key': api_key, 'secret_key': secret_key, 'passphrase': passphrase,
                                      'pseudo': pseudo})
            # queue.put(cli_message)
            print("Adding key", api_key)

        if args.command == 'remove':
            params = args.parameters.strip()
            if len(params) != 1:
                print("Invalid parameters. Expected format: api_key")
                continue
            api_key = params
            cli_message = CliMessage(CliMessage.CliCommand.REMOVE, api_key)
            # queue.put(cli_message)
            print("Removing key", api_key)
            continue


async def main():
    while True:
        next_message = queue.get()
        if isinstance(next_message, WebhookMessage):
            print('Webhook message')
        elif isinstance(next_message, CliMessage):
            print("Cli message :", next_message.content)
