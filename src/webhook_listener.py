import logging

import redis
from flask import Flask, request

from src.objects import WebhookMessage

log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)

app = Flask(__name__)
r = redis.Redis(host='redis')


@app.route('/runbot', methods=['POST'])
def receive_webhook():
    message = request.json
    message = WebhookMessage(message).serialize_message()
    logger.info(f"Received webhook message")
    logger.debug(f'Webhook content : {message}')
    r.rpush('communication', message)
    return 'OK'


if __name__ == '__main__':
    logger.info("Starting webhook listener")
    app.run(host='0.0.0.0', port=5000, debug=True)
