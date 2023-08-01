import os
import pprint
import unittest
from src.order_dispatch import Client
from dotenv import load_dotenv
import logging
load_dotenv()

logger = logging.getLogger(__name__)

class TestOrderDispatch(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = Client(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))

    def test_place_long(self):
        order = {
            'symbol': 'BTCUSDT_UMCBL',
            'marginCoin': 'USDT',
            'size':0.01,
            'side': 'open_long',
            'orderType': 'market',
        }
        size = 0.003
        self.client.place_orders('BTCUSDT_UMCBL','USDT', size, 'open_long', 'market')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[0]['total']) == size
        self.client.place_orders('BTCUSDT_UMCBL', 'USDT', size, 'close_long', 'market')


    def test_place_short(self):
        order = {
            'symbol': 'BTCUSDT_UMCBL',
            'marginCoin': 'USDT',
            'size':0.01,
            'side': 'open_short',
            'orderType': 'market',
        }
        size = 0.003
        self.client.place_orders('BTCUSDT_UMCBL','USDT', size, 'open_short', 'market')
        open_pos = self.client.get_positions('BTCUSDT_UMCBL', 'UMCBL', 'USDT')
        assert float(open_pos[1]['total'])==size
        self.client.place_orders('BTCUSDT_UMCBL','USDT', size, 'close_short', 'market')



