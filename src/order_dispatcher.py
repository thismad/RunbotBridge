import json
import logging
import os
import time

import redis
import requests
from discord_webhook import send_discord_webhook_embed
import consts as c
import exceptions
from objects import CliMessage, Message
import utils


log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)


class BitgetClient():
    """
    Client for the Bitget API
    """
    BITGET_PAIRS = {
        "BTCUSDT": "BTCUSDT_UMCBL",
        "ETHUSDT": "ETHUSDT_UMCBL",
        "XRP-USDT-SWAP": "XRPUSDT_UMCBL"
    }
    BITGET_ORDERS = {
        "long": "open_long",
        "short": "open_short",
    }

    def __init__(self, api_key, api_secret_key, passphrase):
        self.passphrase = passphrase
        self.api_key = api_key
        self.api_secret_key = api_secret_key

    @staticmethod
    def _retry(func):
        """
        Decorator for retrying API calls (Bitget custom)
        :param func:
        :return:
        """

        def wrapper(*args, **kwargs):
            for i in range(2):
                try:
                    sent_time = utils.get_timestamp()
                    result = func(*args, **kwargs)
                    received_time = utils.get_timestamp()
                    logger.info(f'Request took {received_time - sent_time} ms')
                    if result['code'] == '00000':
                        logger.info(f"API call successful")
                        return result
                    else:
                        logger.error(
                            f"API call didnt go through, error code: {result['code']}, error msg: {result['msg']}")
                        continue
                except requests.exceptions.ConnectionError as e:
                    logger.critical(e)
                    time.sleep(7)
                    continue
                except exceptions.BitgetRequestException as e:
                    time.sleep(1)
                    logger.error(e.message)
                    continue
                except exceptions.BitgetAPIException as e:
                    logger.error(e)
                    time.sleep(2)
                    continue
                except Exception as e:
                    logger.error(f"Unknown exception occured: {e}", exc_info=True)
                    continue
            return None

        return wrapper

    @_retry
    def _request(self, method: str, request_path: str, params=None, cursor=False):
        """
        Make a request to the Bitget API
        :param method: str : HTTP method (POST - GET)
        :param request_path: str : Request path
        :param params: dict : Request parameters (uri params or json depending of HTTP method)
        :param cursor: bool : If the request is paginated
        :return: dict : Successful response JSON
        Success response
        {
          "code":"00000",
          "data":{
            "orderId":"1627293504612",
            "clientOid":"BITGET#1627293504612"
          },
          "msg":"success",
          "requestTime":1627293504612
        }

        Failed response
        {
            "code":"40786",
            "msg":"Duplicate clientOid",
            "requestTime":1627293504612
        }

        """
        if method == c.GET:
            request_path = request_path + utils.parse_params_to_str(params)

        # url
        url = c.API_URL + request_path

        # Get local time
        timestamp = utils.get_timestamp()

        body = json.dumps(params) if method == c.POST else ""
        sign = utils.sign(utils.pre_hash(timestamp, method, request_path, str(body)), self.api_secret_key)
        header = utils.get_header(self.api_key, sign, timestamp, self.passphrase)

        # send request
        response = None
        if method == c.GET:
            response = requests.get(url, headers=header)

        elif method == c.POST:
            response = requests.post(url, data=body, headers=header)

        elif method == c.DELETE:
            response = requests.delete(url, headers=header)

        logger.info(f"Called {request_path},response: {response.text}")

        # exception handle
        if not str(response.status_code).startswith('2'):
            raise exceptions.BitgetAPIException(response)
        try:
            res_header = response.headers
            if cursor:
                r = dict()
                try:
                    r['before'] = res_header['BEFORE']
                    r['after'] = res_header['AFTER']
                except:
                    pass
                return response.json(), r
            else:
                return response.json()

        except ValueError:
            raise exceptions.BitgetRequestException('Invalid Response: %s' % response.text)

    def place_orders(self, symbol, margin_coin, size, side, order_type, price='', client_order_id='',
                     reduce_only=False):
        """
        Place order as a trader limited 1c/s as trader or 10c/s if not trader.
        :param symbol:
        :param margin_coin:
        :param size:
        :param side:
        :param order_type:
        :param price:
        :param clientOrderId:
        :param reduceOnly:
        :return: dict : {
                            "orderId":"1627293504612",
                            "clientOid":"BITGET#1627293504612"
                        }  or None if we got an error
        """
        params = {}

        if symbol and margin_coin and size and side and order_type:
            params['symbol'] = symbol
            params['marginCoin'] = margin_coin
            params['size'] = size
            params['side'] = side
            params['orderType'] = order_type
            params['reduceOnly'] = reduce_only
            if price:
                params['price'] = price
            if client_order_id:
                params['clientOid'] = client_order_id

            result = self._request(c.POST, c.MIX_ORDER_V1_URL + '/placeOrder', params)
            if result:
                logger.info(f"Order placed successfully")
                return result['data']
            else:
                logger.error("Failed to place order")
                return None
        else:
            logger.critical("Please check args")
            return None

    def get_positions(self, symbol, product_type, margin_coin=''):
        """
        Get all positions for a symbol and product type
        :param symbol: symbol like in the API doc
        :param product_type: contract type
        :param margin_coin:
        :return: dict : JSON of all positions for a symbol and product type or None if we got an error
        """
        params = {}
        params['symbol'] = symbol
        params['productType'] = product_type
        if margin_coin:
            params['marginCoin'] = margin_coin
        result = self._request(c.GET, c.MIX_POSITION_V1_URL + '/singlePosition', params)
        if result:
            return result['data']
        else:
            logger.error("Failed to get open positions")
            return None

    def close_positions_copy_trading(self, symbol: str, orders_id: list = None, product_type: str = "UMCBL"):
        """
        Close all positions for a symbol and product type
        :param symbol: symbol like in the API doc
        :param orders_id: list of orders id to close
        :param product_type: contract type
        :return: bool : True if all positions are closed, False if not
        """
        logger.info(f"Closing positions for {symbol} with orders id : {orders_id}")
        params = {}
        params['symbol'] = symbol
        params['productType'] = product_type
        params['pageNo'] = 1
        params['pageSize'] = 50
        #TODO Might have to iterate on it if we have nore than 50 pos
        resp = self._request(c.GET, c.MIX_TRACE_V1_URL + '/currentTrack', params)
        if resp:
            # List of all open positions
            open_positions = resp['data']
            # Calculate nb of open positions for a symbol (API sends a JSON with both short and long sides with total = 0 if closed or >0 if opened)
            nb_open_positions = len(open_positions)
            logger.info(f"Open positions:{nb_open_positions}")
        else:
            logger.error("Failed to get open positions")
            return False

        if nb_open_positions == 0:
            return True
        else:
            # Close positions by order id
            if orders_id:
                for order_id in orders_id:
                    for open_position in open_positions:
                        # If order id is in open positions then we close it
                        if open_position['openOrderId'] == order_id:
                            result = self._request(c.POST, c.MIX_TRACE_V1_URL + '/closeTrackOrder',
                                                   {'symbol': symbol, 'trackingNo': open_position['trackingNo']})
                            if result:
                                logger.info(f"Closed position {order_id}")
                                break
                            else:
                                logger.error(f"Failed to close position {order_id}")
                                return False

            # Close all positions for symbol if no orders list is provided
            else:
                for pos in resp['data']:
                    result = self._request(c.POST, c.MIX_TRACE_V1_URL + '/closeTrackOrder',
                                           {'symbol': symbol, 'trackingNo': pos['trackingNo']})
                    if result:
                        logger.info(f"Closed position {pos['trackingNo']}")
                    else:
                        logger.error(f"Failed to close position {pos['trackingNo']}")
                        return False
        return True

    def start(self, r):
        """
        Start the order dispatcher
        :return:
        """
        # Read settings
        with open('settings.json') as f:
            settings = json.load(f)
        activated_pairs = settings['activated-pairs']

        running = True
        r = redis.Redis(host='redis')
        while True:
            message = r.blpop('communication', 0)[1]
            message = Message.deserialize_message(message)
            logger.info(f"Received message: {message}")
            if isinstance(message, CliMessage):
                if message.command == CliMessage.CliCommand.RESUME:
                    running = True
                    logger.info("Resuming order dispatcher")
                    pass
                elif message.command == CliMessage.CliCommand.PAUSE:
                    running = False
                    logger.info("Pausing order dispatcher")
                elif message.command == CliMessage.CliCommand.EXIT:
                    success = False
                    for pair in activated_pairs:
                        success = self.close_positions_copy_trading(self.BITGET_PAIRS[pair])
                    if success:
                        running = False
                        # Clear redis database from all the orders
                        r.flushdb()
                        logger.info("All positions closed, exiting order dispatcher")
                    else:
                        logger.error("Failed to close all positions, not exiting order dispatcher")

            else:
                if running:
                    self.order_logic(r, message, activated_pairs)
                else:
                    logger.info("Received order but order dispatcher has been paused, not passing orders")

    def order_logic(self, r, message, activated_pairs):
        """
        Logic for placing orders
        :param r: redis.Redis : Redis connection
        :param message: Message : Message received from the websocket
        :param activated_pairs: list : List of activated pairs
        :return:
        """

        symbol = message.content['market']
        success = False
        order = None

        if symbol in activated_pairs:
            position_id = message.content['positionId']
            position_type = message.content['positionType']
            symbol = self.BITGET_PAIRS[symbol]
            margin_coin = 'USDT'
            size = message.content['size']
            side = message.content['tradeDirection']
            side = self.BITGET_ORDERS[side]
            order_type = 'market'

            if position_type == 'open' or position_type == 'increase':
                logger.info(f"Received {message.content['positionType']} order, passing order")
                order = self.place_orders(symbol, margin_coin, size, side, order_type)
                if order:
                    order_id = order['orderId']
                    utils.insert_order_redis(r, position_id, order_id)

            elif position_type == 'decrease':
                logger.info("Received decrease order, passing order")
                # Inverse side for decrease order
                side = self.BITGET_ORDERS['long'] if side == self.BITGET_ORDERS['short'] else \
                    self.BITGET_ORDERS[
                        'short']
                order = self.place_orders(symbol, margin_coin, size, side, order_type)
                if order:
                    order_id = order['orderId']
                    utils.insert_order_redis(r, position_id, order_id)

            elif position_type == 'close':
                logger.info("Received close order, passing order")
                # Try to get orders id from redis, possibility that there is no orders id if we have a close order and bot didnt receive an open order before
                try:
                    orders_id = json.loads(r.get(position_id))
                    # If there are no corresponding order id, it means that the bot didnt open any trade anyway, r.get returns None
                except TypeError:
                    logger.error(f'No corresponding orders for strategy id: {position_id}, could not pass the close order')
                    pass
                else:
                    success = self.close_positions_copy_trading(symbol, orders_id)
                    if success:
                        # Remove all closed orders from redis
                        utils.remove_orders_redis(r, position_id, orders_id)
            else:
                logger.error(f"Unknown position type: {position_type}")

            if success or order:
                send_discord_webhook_embed(os.getenv('TBF_WEBHOOK_URL'), message.content['price'],
                                           message.content['market'], message.content['tradeDirection'],
                                           message.content['positionType'], message.content['t'])

        else:
            logger.info(f"Received order for {symbol} but not activated, not passing order")
        pass


if __name__ == '__main__':
    client = BitgetClient(os.getenv('API_KEY'), os.getenv('API_SECRET'),
                          os.getenv('PASSPHRASE'))
    r = redis.Redis(host=os.getenv('REDIS_HOST'))
    client.start(r)

