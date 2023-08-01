from src.objects import WebhookMessage
import logging
from flask import Flask, request
from multiprocessing import Queue, Process
import redis

logger = logging.getLogger(__name__)

app = Flask(__name__)
r = redis.Redis()

@app.route('/runbot', methods=['POST'])
def receive_webhook():
    r.rpush('communication', request.json)
    return 'OK'

