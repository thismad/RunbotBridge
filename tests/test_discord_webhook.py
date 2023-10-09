import os
import unittest
from discord_webhook import send_discord_webhook_embed
from objects import WebhookMessage
class TestDiscordWebhook(unittest.TestCase):
    def test_send_discord_webhook_open_short(self):
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "open",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "short",
            "price": "28911.90",
            "size": "0.0001",
            "leverage": "0.86736"
        })
        success =send_discord_webhook_embed(os.getenv('TBF_WEBHOOK_URL_STAGING'), webhook_open_long.content['price'], webhook_open_long.content['market'], webhook_open_long.content['tradeDirection'], webhook_open_long.content['positionType'], webhook_open_long.content['t'])
        assert success == True

    def test_send_discord_webhook_open_long(self):
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "open",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "long",
            "price": "28911.90",
            "size": "0.0001",
            "leverage": "0.86736"
        })
        success = send_discord_webhook_embed(os.getenv('TBF_WEBHOOK_URL_STAGING'), webhook_open_long.content['price'],
                                             webhook_open_long.content['market'],
                                             webhook_open_long.content['tradeDirection'],
                                             webhook_open_long.content['positionType'], webhook_open_long.content['t'])
        assert success == True

    def test_send_discord_webhook_close_short(self):
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "close",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "short",
            "price": "28911.90",
            "size": "0.0001",
            "leverage": "0.86736"
        })
        success = send_discord_webhook_embed(os.getenv('TBF_WEBHOOK_URL_STAGING'), webhook_open_long.content['price'],
                                             webhook_open_long.content['market'],
                                             webhook_open_long.content['tradeDirection'],
                                             webhook_open_long.content['positionType'], webhook_open_long.content['t'])
        assert success == True

    def test_send_discord_webhook_close_long(self):
        webhook_open_long = WebhookMessage({
            "exchange": "Binance",
            "market": "BTCUSDT",
            "t": 1611192000000,
            "positionType": "close",
            "positionId": "1",
            "orderType": "market",
            "tradeDirection": "long",
            "price": "28911.90",
            "size": "0.0001",
            "leverage": "0.86736"
        })
        success = send_discord_webhook_embed(os.getenv('TBF_WEBHOOK_URL_STAGING'), webhook_open_long.content['price'],
                                             webhook_open_long.content['market'],
                                             webhook_open_long.content['tradeDirection'],
                                             webhook_open_long.content['positionType'], webhook_open_long.content['t'])
        assert success == True
