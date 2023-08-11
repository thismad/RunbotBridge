import json
import logging

logger = logging.getLogger(__name__)


class ApiKey:
    def __init__(self, api_key, api_secret_key, passphrase, pseudo):
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.passphrase = passphrase
        self.pseudo = pseudo


class KeyHandler:
    def __init__(self, filepath: str = '../keys.json'):
        self.keys = {}
        self.filepath = filepath
        self.keys = self._read_keys()

    def _read_keys(self) -> dict[ApiKey]:
        """
        Read keys from json file
        :param filepath: string : filepath to stored json containing the keys
        :return: dict[ApiKey] : Dict of ApiKey objects
        """
        keys = {}
        print('path', self.filepath)
        with open(self.filepath, 'r') as f:
            keys_json = json.load(f)
            for key_hash, value in keys_json.items():
                # Can't have two keys with same pub key (shouldnt happen tho)
                if keys.get(key_hash) is None:
                    keys.update({key_hash: ApiKey(
                        key_hash,
                        value['api_secret'],
                        value['passphrase'],
                        value['pseudo']
                    )})
                else:
                    logger.error('Key already exists')
        return keys

    def remove_key(self, key: ApiKey):
        """
        Remove a key from the handler
        :param key: ApiKey : Key object to remove from handler
        :return:
        """
        self.keys.pop(key.api_key)
        logger.info(f'Key {key} removed from handler')

    def add_key(self, key: ApiKey):
        """
        Add a key to the handler
        :param key: ApiKey : Key object to add to handler
        :return:
        """
        if self.keys.get(key.api_key) is None:
            self.keys.update({key.api_key: key})
            logger.info(f'Key {key.api_key} added to handler')
        else:
            logger.error('Key already exists in handler')

    def _save_keys(self):
        """
        Save keys to json file
        :return:
        """
        json_to_save = {}
        for key_hash, key in self.keys.items():
            json_to_save.update({key_hash: {
                'api_secret_key': key.api_secret_key,
                'passphrase': key.passphrase,
                'pseudo': key.pseudo
            }})

        with open(self.filepath, 'w') as f:
            json.dump(json_to_save, f)
            logger.info('Keys saved to file')
