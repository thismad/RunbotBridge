import json
import logging
import os
import unittest
from unittest.mock import patch, MagicMock

from dotenv import load_dotenv

from src.objects import WebhookMessage
from src.order_dispatcher import BitgetClient

load_dotenv()

logger = logging.getLogger(__name__)


class RealTestOrderDispatch(unittest.TestCase):
    """
    This class tests the order dispatcher with a real Bitget client and real orders.
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
        # Size of 0.01 $BTC
        cls.size = 0.01

    def test_place_long(self):
        # order = {
        #     'symbol': 'BTCUSDT_UMCBL',
        #     'marginCoin': 'USDT',
        #     'size':0.01,
        #     'side': 'open_long',
        #     'orderType': 'market',
        # }
        self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_long', 'market')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == self.size

        self.client.close_positions_copy_trading('BTCUSDT_UMCBL')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == 0
        assert float(open_pos[1]['total']) == 0

    def test_add_to_long(self):
        size_to_add = 0.01
        # Entering long
        self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_long', 'market')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == self.size

        # Add to long
        self.client.place_orders('BTCUSDT_UMCBL', 'USDT', size_to_add, 'open_long', 'market')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == self.size + size_to_add

        self.client.close_positions_copy_trading('BTCUSDT_UMCBL')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == 0
        assert float(open_pos[1]['total']) == 0

    def test_place_short(self):
        # order = {
        #     'symbol': 'BTCUSDT_UMCBL',
        #     'marginCoin': 'USDT',
        #     'size':0.01,
        #     'side': 'open_short',
        #     'orderType': 'market',
        # }
        self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[1]['total']) == self.size

        self.client.close_positions_copy_trading('BTCUSDT_UMCBL')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == 0
        assert float(open_pos[1]['total']) == 0

    def test_add_to_short(self):
        size_to_add = 0.01
        self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[1]['total']) == self.size

        self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[1]['total']) == self.size + size_to_add

        self.client.close_positions_copy_trading('BTCUSDT_UMCBL')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == 0
        assert float(open_pos[1]['total']) == 0

    def test_short_and_long(self):
        self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')
        self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_long', 'market')

        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == self.size
        assert float(open_pos[1]['total']) == self.size

        self.client.close_positions_copy_trading('BTCUSDT_UMCBL')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == 0
        assert float(open_pos[1]['total']) == 0

    def test_close_positions_copy_trading_only_one_strategy(self):
        order1 = self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')
        order2 = self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')

        order_id_1 = order1['orderId']
        order_id_2 = order2['orderId']

        self.client.close_positions_copy_trading('BTCUSDT_UMCBL', [order_id_1, order_id_2])
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == 0
        assert float(open_pos[1]['total']) == 0

    def test_close_positions_copy_trading_one_strategy_on_two(self):
        order1 = self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')
        order2 = self.client.place_orders('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')

        order_id_1 = order1['orderId']
        order_id_2 = order2['orderId']

        self.client.close_positions_copy_trading('BTCUSDT_UMCBL', [order_id_1, order_id_2])
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == 0
        assert float(open_pos[1]['total']) == 0


class MockTestOrderDispatch(unittest.TestCase):
    """
    A class to test the order dispatcher using mock components.
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
        # Size of 0.01 $BTC
        cls.size = 0.01

    @staticmethod
    def mock_redis_queue(queue_data: list, data_store: dict):
        """
        A helper function to create a mock Redis queue.
        """
        mock_queue = MagicMock()

        # Configure the mock rpush method to append data to the queue
        mock_queue.rpush.side_effect = queue_data.append

        mock_queue.set.side_effect = data_store.__setitem__
        mock_queue.get.side_effect = data_store.get

        # Configure the mock blpop method to block until there's data, then return and remove the first item
        mock_queue.blpop.side_effect = lambda _, __: (None, queue_data.pop(0)) if queue_data else None

        return mock_queue

    @patch('redis.Redis', autospec=True)
    @patch('src.order_dispatcher.BitgetClient.place_orders')
    def test_order_logic_open_long(self, mock_place_orders, redis_mock):
        queue_data = []
        store_data = {}
        r_mock = self.mock_redis_queue(queue_data, store_data)
        redis_mock.return_value = r_mock
        order_id = "14193209138"
        activated_pairs = ['BTCUSDT', 'ETHUSDT']
        mock_place_orders.return_value = {
            "orderId": order_id,
            "clientOid": "BITGET#1627293504612"
        }
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "open",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "long",
            "price": "28911.90",
            "size": self.size,
            "leverage": "0.86736"
        })
        r_mock.rpush(webhook_open_long.serialize_message())

        bitget_client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
        bitget_client.order_logic(r_mock, webhook_open_long, activated_pairs=activated_pairs)

        # We are expecting an order to be placed and the order id to be returned
        mock_place_orders.assert_called_with('BTCUSDT_UMCBL', 'USDT', self.size, 'open_long', 'market')
        assert json.loads(r_mock.get('1')) == [order_id]

    @patch('redis.Redis', autospec=True)
    @patch('src.order_dispatcher.BitgetClient.place_orders')
    def test_order_logic_open_short(self, mock_place_orders, redis_mock):
        queue_data = []
        store_data = {}
        r_mock = self.mock_redis_queue(queue_data, store_data)
        redis_mock.return_value = r_mock
        order_id = "14193209138"
        activated_pairs = ['BTCUSDT', 'ETHUSDT']
        mock_place_orders.return_value = {
            "orderId": order_id,
            "clientOid": "BITGET#1627293504612"
        }
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "open",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "short",
            "price": "28911.90",
            "size": self.size,
            "leverage": "0.86736"
        })
        r_mock.rpush(webhook_open_long.serialize_message())

        bitget_client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
        bitget_client.order_logic(r_mock, webhook_open_long, activated_pairs=activated_pairs)

        # We are expecting an order to be placed and the order id to be returned
        mock_place_orders.assert_called_with('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')
        assert json.loads(r_mock.get('1')) == [order_id]

    @patch('redis.Redis', autospec=True)
    @patch('src.order_dispatcher.BitgetClient.place_orders')
    def test_order_logic_increase_long(self, mock_place_orders, redis_mock):
        # Init
        queue_data = []
        store_data = {}
        bitget_client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
        r_mock = self.mock_redis_queue(queue_data, store_data)
        redis_mock.return_value = r_mock

        # Place first long
        order_id = "14193209138"
        activated_pairs = ['BTCUSDT', 'ETHUSDT']
        mock_place_orders.return_value = {
            "orderId": order_id,
            "clientOid": "BITGET#1627293504612"
        }
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "open",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "long",
            "price": "28911.90",
            "size": self.size,
            "leverage": "0.86736"
        })
        r_mock.rpush(webhook_open_long.serialize_message())

        bitget_client.order_logic(r_mock, webhook_open_long, activated_pairs=activated_pairs)

        # Place second long thus increasing position
        order_id_2 = "14193209139"
        activated_pairs = ['BTCUSDT', 'ETHUSDT']
        mock_place_orders.return_value = {
            "orderId": order_id_2,
            "clientOid": "BITGET#1627293504612"
        }
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "increase",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "long",
            "price": "28911.90",
            "size": self.size,
            "leverage": "0.86736"
        })
        r_mock.rpush(webhook_open_long.serialize_message())
        bitget_client.order_logic(r_mock, webhook_open_long, activated_pairs=activated_pairs)
        mock_place_orders.assert_called_with('BTCUSDT_UMCBL', 'USDT', self.size, 'open_long', 'market')

        assert json.loads(r_mock.get('1')) == [order_id, order_id_2]

    @patch('redis.Redis', autospec=True)
    @patch('src.order_dispatcher.BitgetClient.place_orders')
    def test_order_logic_increase_shprt(self, mock_place_orders, redis_mock):
        # Init
        queue_data = []
        store_data = {}
        bitget_client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
        r_mock = self.mock_redis_queue(queue_data, store_data)
        redis_mock.return_value = r_mock

        # Place first long
        order_id = "14193209138"
        activated_pairs = ['BTCUSDT', 'ETHUSDT']
        mock_place_orders.return_value = {
            "orderId": order_id,
            "clientOid": "BITGET#1627293504612"
        }
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "open",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "short",
            "price": "28911.90",
            "size": self.size,
            "leverage": "0.86736"
        })
        r_mock.rpush(webhook_open_long.serialize_message())

        bitget_client.order_logic(r_mock, webhook_open_long, activated_pairs=activated_pairs)

        # Place second long thus increasing position
        order_id_2 = "14193209139"
        activated_pairs = ['BTCUSDT', 'ETHUSDT']
        mock_place_orders.return_value = {
            "orderId": order_id_2,
            "clientOid": "BITGET#1627293504612"
        }
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "increase",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "short",
            "price": "28911.90",
            "size": self.size,
            "leverage": "0.86736"
        })
        r_mock.rpush(webhook_open_long.serialize_message())
        bitget_client.order_logic(r_mock, webhook_open_long, activated_pairs=activated_pairs)
        mock_place_orders.assert_called_with('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')

        assert json.loads(r_mock.get('1')) == [order_id, order_id_2]

    @patch('redis.Redis', autospec=True)
    @patch('src.order_dispatcher.BitgetClient.place_orders')
    def test_order_logic_decrease_long(self, mock_place_orders, redis_mock):
        # Init
        queue_data = []
        store_data = {}
        bitget_client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
        r_mock = self.mock_redis_queue(queue_data, store_data)
        redis_mock.return_value = r_mock

        # Place first long
        order_id = "14193209138"
        activated_pairs = ['BTCUSDT', 'ETHUSDT']
        mock_place_orders.return_value = {
            "orderId": order_id,
            "clientOid": "BITGET#1627293504612"
        }
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "decrease",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "short",
            "price": "28911.90",
            "size": self.size,
            "leverage": "0.86736"
        })
        r_mock.rpush(webhook_open_long.serialize_message())

        bitget_client.order_logic(r_mock, webhook_open_long, activated_pairs=activated_pairs)
        mock_place_orders.assert_called_with('BTCUSDT_UMCBL', 'USDT', self.size, 'open_long', 'market')
        assert json.loads(r_mock.get('1')) == [order_id]

    @patch('redis.Redis', autospec=True)
    @patch('src.order_dispatcher.BitgetClient.place_orders')
    def test_order_logic_decrease_short(self, mock_place_orders, redis_mock):
        # Init
        queue_data = []
        store_data = {}
        bitget_client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
        r_mock = self.mock_redis_queue(queue_data, store_data)
        redis_mock.return_value = r_mock

        # Place first long
        order_id = "14193209138"
        activated_pairs = ['BTCUSDT', 'ETHUSDT']
        mock_place_orders.return_value = {
            "orderId": order_id,
            "clientOid": "BITGET#1627293504612"
        }
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "decrease",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "long",
            "price": "28911.90",
            "size": self.size,
            "leverage": "0.86736"
        })
        r_mock.rpush(webhook_open_long.serialize_message())

        bitget_client.order_logic(r_mock, webhook_open_long, activated_pairs=activated_pairs)
        mock_place_orders.assert_called_with('BTCUSDT_UMCBL', 'USDT', self.size, 'open_short', 'market')
        assert json.loads(r_mock.get('1')) == [order_id]

    @patch('redis.Redis', autospec=True)
    @patch('src.order_dispatcher.BitgetClient.place_orders')
    @patch('src.order_dispatcher.BitgetClient.close_positions_copy_trading')
    def test_order_logic_close_strategy(self, mock_close_pos, mock_place_orders, redis_mock):
        # Init
        queue_data = []
        store_data = {}
        bitget_client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
        r_mock = self.mock_redis_queue(queue_data, store_data)
        redis_mock.return_value = r_mock

        # Create close orders for strategy 1 message
        order_id = "14193209138"
        order_id_2 = "14193209139"
        activated_pairs = ['BTCUSDT', 'ETHUSDT']
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "close",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "short",
            "price": "28911.90",
            "size": self.size,
            "leverage": "0.86736"
        })

        # Add two orders id to strategy 1 (2 running trades)
        r_mock.set('1', json.dumps([order_id, order_id_2]))

        # Push close orders for strategy 1 on redis
        r_mock.rpush(webhook_open_long.serialize_message())

        # Call order logic
        bitget_client.order_logic(r_mock, webhook_open_long, activated_pairs=activated_pairs)
        mock_close_pos.assert_called_with('BTCUSDT_UMCBL', [order_id, order_id_2])
        assert json.loads(r_mock.get('1')) == []

    # TODO : Test to open position if script is paused
