import base64
import hmac
import json
import time

from . import consts as c


def sign(message, secret_key):
    """
    Sign the message
    :param message:
    :param secret_key:
    :return:
    """
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d)


def pre_hash(timestamp, method, request_path, body):
    return str(timestamp) + str.upper(method) + request_path + body


def get_header(api_key, sign, timestamp, passphrase):
    """
    Get header for request
    :param api_key:
    :param sign:
    :param timestamp:
    :param passphrase:
    :return:
    """
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON
    header[c.ACCESS_KEY] = api_key
    header[c.ACCESS_SIGN] = sign
    header[c.ACCESS_TIMESTAMP] = str(timestamp)
    header[c.ACCESS_PASSPHRASE] = passphrase
    # header[c.LOCALE] = 'zh-CN'

    return header


def parse_params_to_str(params):
    """
    Parse params to uri string
    :param params:
    :return:
    """
    url = '?'
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'
    return url[0:-1]


def insert_order_redis(r, key, value):
    """
    Append an order to the list of orders for a position id AKA a strategy id
    :param r: redis.Redis : Redis connection object
    :param key: str : key to set
    :param value: str : value to set
    :return:
    """
    orders = r.get(key)
    # If strategy id exists, append order to the list
    if orders:
        orders = json.loads(orders)
        orders.append(value)
        r.set(key, json.dumps(orders))
    # If strategy id does not exist, create a new list and add the new order
    else:
        orders = [value]
        r.set(key, json.dumps(orders))


def remove_orders_redis(r, key, values: list):
    """
    Remove an order from the list of orders for a position id AKA a strategy id
    :param r: redis.Redis : Redis connection object
    :param key: str : key
    :param value: list : values to remove
    :return:
    """
    orders = r.get(key)
    # If strategy id exists, remove order from the list
    if orders:
        orders = json.loads(orders)
        for value in values:
            orders.remove(value)
        r.set(key, json.dumps(orders))
    # If strategy id does not exist, do nothing
    else:
        pass


def get_timestamp():
    return int(time.time() * 1000)

