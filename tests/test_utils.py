import unittest
from unittest.mock import MagicMock

from src.utils import insert_order_redis, remove_orders_redis


class TestUtils(unittest.TestCase):

    @staticmethod
    def mock_redis_queue(data_store: dict):
        """
        A helper function to create a mock Redis queue.
        """
        mock_queue = MagicMock()

        mock_queue.set.side_effect = data_store.__setitem__
        mock_queue.get.side_effect = data_store.get

        return mock_queue

    def test_insert_order_redis_add_first_order(self):
        r_mock = self.mock_redis_queue({})
        insert_order_redis(r_mock, '1', 5)
        print(r_mock.get('1'))
        assert r_mock.get('1') == '[5]'

    def test_insert_order_redis_add_second_order(self):
        r_mock = self.mock_redis_queue({'1': '[5]'})
        insert_order_redis(r_mock, '1', 6)
        assert r_mock.get('1') == '[5, 6]'

    def test_remove_orders_redis_remove_one_order(self):
        data_store = {}
        r_mock = self.mock_redis_queue(data_store)
        r_mock.set('1', '[5, 6]')
        print(r_mock.get('1'))
        remove_orders_redis(r_mock, '1', [5])
        assert r_mock.get('1') == '[6]'

    def test_remove_orders_redis_remove_multiple_orders(self):
        data_store = {}
        r_mock = self.mock_redis_queue(data_store)
        r_mock.set('1', '[5, 6]')
        remove_orders_redis(r_mock, '1', [5, 6])
        assert r_mock.get('1') == '[]'
