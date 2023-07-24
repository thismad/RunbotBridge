import unittest
import os
import json
from src.handle_keys import ApiKey, KeyHandler

class TestKeyHandler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        keys_path = 'test_keys.json'
        keys_json = {
            "key1": {
                "api_secret": "xsxex",
                "passphrase": "xsxex",
                "pseudo": "maurice"
            },
            "key2": {
                "api_secret": "xsxex",
                "passphrase": "xsxex",
                "pseudo": "yala"
            },
        }
        with open(keys_path, 'w') as f:
            json.dump(keys_json, f)

        cls.key_handler = KeyHandler(keys_path)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        os.remove('test_keys.json')

    def test_add_key(self):
        key = ApiKey(
            'key3',
            'xsxex',
            'xsxex',
            'xsxex'
        )
        self.key_handler.add_key(key)
        assert self.key_handler.keys.get('key3') is not None
        self.key_handler.remove_key(key)

    def test_remove_key(self):
        key = ApiKey(
            'key3',
            'xsxex',
            'xsxex',
            'xsxex'
        )
        self.key_handler.add_key(key)
        self.key_handler.remove_key(key)
        assert self.key_handler.keys.get('key3') is None

    def test_save_keys(self):
        key = ApiKey(
            'key3',
            'xsxex',
            'xsxex',
            'xsxex'
        )
        self.key_handler.add_key(key)
        self.key_handler._save_keys()
        with open('test_keys.json', 'r') as f:
            keys_json = json.load(f)
            assert keys_json.get('key3') is not None

    def test_read_keys(self):
        key_handler = KeyHandler('test_keys.json')
        assert key_handler.keys.get('key1') is not None
        assert key_handler.keys.get('key2') is not None
        assert key_handler.keys.get('key3') is None