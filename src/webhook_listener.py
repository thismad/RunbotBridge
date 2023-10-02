import logging
from dotenv import load_dotenv
import redis
from flask import Flask, request
import os
from src.objects import WebhookMessage

load_dotenv()
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)

if os.getenv('ENV') == 'staging':
    logger.info("Starting webhook listener in staging mode")
    r = redis.Redis(host=os.getenv('REDIS_HOST_STAGING'))
elif os.getenv('ENV') == 'production':
    logger.info("Starting webhook listener in production mode")
    r = redis.Redis(host=os.getenv('REDIS_HOST_PRODUCTION'))
else:
    logger.error("Please set ENV to production or staging, aborting order dispatcher")
    exit(1)

app = Flask(__name__)


@app.route('/runbot', methods=['POST'])
def receive_webhook():
    message = request.json
    message = WebhookMessage(message).serialize_message()
    logger.info(f"Received webhook message")
    logger.debug(f'Webhook content : {message}')
    r.rpush('communication', message)
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
