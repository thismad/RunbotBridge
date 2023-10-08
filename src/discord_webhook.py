import datetime

import requests
from consts import RED, GREEN
import logging

logger = logging.getLogger(__name__)


def send_discord_webhook_embed(url, price: str, market: str, trade_direction: str, position_type: str, timestamp: int):
    """
    Send a Discord webhook with embeds
    :param url:
    :param embeds:
    :return:
    """
    color = GREEN if trade_direction == "long" else RED
    trade_direction = "long" if trade_direction == "short" else "short" if position_type == "close" else trade_direction
    trade_embed = {"embeds": [{
        "color": color,
        "author": {
            "name": f"Runbot alert",
            "icon_url": "https://runbot.io/static/image/runbot_logo.png?1"
        },
        "title": f"{position_type.capitalize()} {trade_direction} trade",
        "icon": 'https://runbot.io/static/image/runbot_logo.png?1',
        "thumbnail": {
            "url": 'https://runbot.io/static/image/runbot_logo.png?1'
        },
        "fields": [{
            "name": "Strategy name",
            "value": 'Alphabot',
            "inline": False
        },
            {
                "name": "Market",
                "value": f"{market}",
                "inline": True
            },
            {
                "name": "Price",
                "value": f"{price:.1f}",
                "inline": True
            }
        ],
        "footer": {
            "text": f"Algo running with Runbot.io - {datetime.datetime.fromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')}"
        },
    },
    ]}
    try:
        resp = requests.post(url,
                             json=trade_embed)
        if resp.status_code == 200 or resp.status_code == 204:
            logger.debug(f"Successfuly posted on discord")
            return True
        else:
            logger.error(f"Error while posting on discord : {resp.status_code}, {resp.text}")
    except Exception as e:
        logger.error(f"Error while posting discord : {e}")
    return False
