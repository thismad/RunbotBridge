import json
import os
import time
import requests

import src.consts as c

import aiohttp
import logging

from objects import Message, CliMessage, WebhookMessage

logger = logging.getLogger(__name__)

from src import utils, exceptions
import redis

r = redis.Redis()


class Client():
    def __init__(self, api_key, api_secret_key, passphrase):
        self.passphrase = passphrase
        self.api_key = api_key
        self.api_secret_key = api_secret_key

    @staticmethod
    def _retry(func):
        def wrapper(*args, **kwargs):
            for i in range(2):
                try:
                    sent_time = utils.get_timestamp()
                    result = func(*args, **kwargs)
                    received_time = utils.get_timestamp()
                    logger.info(f'Request took {received_time - sent_time} seconds')
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
                    continue
                except Exception as e:
                    logger.error(f"Unknown exception occured: {e}", exc_info=True)
                return None

        return wrapper

    @_retry
    def _request(self, method, request_path, params, cursor=False):
        """
        :param method:
        :param request_path:
        :param params:
        :param cursor:
        :return: JSON : Successful response JSON
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
            logger.info(f"Called {request_path}, response: {response.text}")

        elif method == c.POST:
            response = requests.post(url, data=body, headers=header)
            logger.info(f"Called {request_path},response: {response.text}")

        elif method == c.DELETE:
            response = requests.delete(url, headers=header)

        logger.info(f"Called {request_path} status: {response.status_code}")
        # exception handle
        if not str(response.status_code).startswith('2'):
            raise exceptions.BitgetAPIException(response)
        print(response.json())
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
        Place order as a trader limited 1c/s or 10c/s if not trader.
        :param symbol:
        :param margin_coin:
        :param size:
        :param side:
        :param order_type:
        :param price:
        :param clientOrderId:
        :param reduceOnly:
        :return: dict : If order is opened successfully, return order id {
            "orderId":"1627293504612",
            "clientOid":"BITGET#1627293504612"
          }
          else return None
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
            return result['data']
        else:
            logger.critical("Please check args")
            return None

    def get_positions(self, symbol, product_type, margin_coin=''):
        """
        Get all positions for a symbol and product type
        :param symbol: symbol like in the API doc
        :param product_type: contract type
        :param margin_coin:
        :return: dict : JSON of all positions for a symbol and product type
        """
        params = {}
        params['symbol'] = symbol
        params['productType'] = product_type
        if margin_coin:
            params['marginCoin'] = margin_coin
        result = self._request(c.GET, c.MIX_POSITION_V1_URL + '/singlePosition', params)
        return result['data']

    def close_positions(self, symbol, product_type: str = "UMCBL"):
        """
        Close all positions for a symbol and product type
        :param symbol: symbol like in the API doc
        :param product_type: contract type
        :return: bool : True if all positions are closed, False if not
        """
        params = {}
        params['symbol'] = symbol
        params['productType'] = product_type
        params['pageNo'] = 1
        params['pageSize'] = 50
        resp = self._request(c.POST, c.MIX_TRACE_V1_URL + '/currentTrack', params)

        # List of all open positions
        open_positions = resp['data']

        if len(open_positions) == 0:
            return True
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

    def start(self):
        """
        Start the order dispatcher
        :return: None
        """
        while True:
            # Pop first item or wait indifinitely
            message = r.blpop('communication', 0)[1]
            message = Message.deserialize_message(message)
            # if isinstance(message, WebhookMessage):
            #     # TODO pass orders
            # elif isinstance(message, CliMessage):
            #     # TODO pause stop all processes?
            # else:
            #     logger.error(f"Unknown message type {message}")

            # TODO : check messages and pass orders

if __name__ == '__main__':
    client = Client(os.getenv('API_KEY'), os.getenv('API_SECRET'), os.getenv('PASSPHRASE'))
    logger.info("Starting order dispatcher")
    client.start()