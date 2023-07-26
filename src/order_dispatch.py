# Runbot webhook example
# {
#    "exchange": "Bitget",
#    "market": "BNBUSDT_UMCBL",
#    "t": "1687790326",
#    "positionType": "reduce",
#    "positionId": "16770000",
#    "orderType": "market",
#    "tradeDirection": "long",
#    "positionMode": "hedged",
#    "size": "0.81",
#    "leverage": "0.66641",
#    "price": "29972"
# }
import json
import time

from symbol import decorator

import requests

import src.consts as c

import aiohttp
import logging

logger = logging.getLogger(__name__)

from src import utils, exceptions


class Client():
    def __init__(self, api_key, api_secret_key, passphrase):
        self.passphrase = passphrase
        self.api_key = api_key
        self.api_secret_key = api_secret_key

    def _retry(self, func):
        def wrapper(*args, **kwargs):
            for i in range(2):
                try:
                    sent_time = utils.get_timestamp()
                    result = func(*args, **kwargs)
                    received_time = utils.get_timestamp()
                    logger.info(f'Request took {received_time - sent_time} seconds')
                    if result['code'] == '00000':
                        logger.info(f"Order went through, order id: {result['data']['orderId']}")
                        return result['data']
                    else:
                        logger.error(
                            f"Order didnt go through, error code: {result['code']}, error msg: {result['msg']}")
                        continue
                except requests.exceptions.ConnectionError as e:
                    logger.critical(e)
                    time.sleep(7)
                    continue
                except exceptions.BitgetRequestException as e:
                    time.sleep(1)
                    logger.error(e)
                    continue
                except exceptions.BitgetAPIException as e:
                    logger.error(e)
                    continue
                except Exception as e:
                    logger.error("Unknown exception occured: ", e)

    @_retry
    async def _request(self, method, request_path, params, cursor=False):
        '''

        :param method:
        :param request_path:
        :param params:
        :param cursor:
        :return: Successful response
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

        '''
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
            logger.info(f"Called {request_path}, response :", response.text)
        elif method == c.POST:
            response = requests.post(url, data=body, headers=header)
            logger.info(f"Called {request_path},response :", response.text)

        elif method == c.DELETE:
            response = requests.delete(url, headers=header)

        logger.info(f"Called {request_path} status :", response.status_code)
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

    def place_orders(self, symbol, quantity, side, orderType, force, price='', clientOrderId=''):
        '''
        Place order as a trader limited 1c/s or 10c/s if not trader.
        :param symbol:
        :param quantity:
        :param side:
        :param orderType:
        :param force:
        :param price:
        :param clientOrderId:
        :return: dict : If order is opened successfully, return order id {
            "orderId":"1627293504612",
            "clientOid":"BITGET#1627293504612"
          }
          else return None
        '''
        params = {}

        if symbol and quantity and side and orderType and force:
            params["symbol"] = symbol
            params["price"] = price
            params["quantity"] = quantity
            params["side"] = side
            params["orderType"] = orderType
            params["force"] = force
            params["clientOrderId"] = clientOrderId
            return self._request(c.POST, c.MIX_ORDER_V1_URL + '/orders', params)
        else:
            logger.critical("Please check args")
            return None
