import os
import sys
import app.helpers


ANNOUNCEMENTS_SUBFORUM = "https://www.havenandhearth.com/forum/viewforum.php?f=39"
TITLE_PAGE = "https://www.havenandhearth.com/portal/"
FORUM_LINK="https://www.havenandhearth.com/forum"

RUN_DATA_PATH = "run_data"
TG_ID_FILE = "tg_users"
DISCORD_WEBHOOK_FILE = "discord_webhooks"
SERVER_STATUS_FILE = "server_status"
UP_MESSAGE = "Both servers are up"

POLLING_INTERVAL = 60


def get_token():
    try:
        token = os.environ['TG_TOKEN']
    except KeyError:
        app.helpers.app_logger.error('Missing TG_TOKEN env varbiable')
        sys.exit(1)
    return token


def get_bot_admin():
    try:
        admin_id = int(os.environ['BOT_ADMIN'])
    except (KeyError, ValueError):
        app.helpers.app_logger.error('Missing BOT_ADMIN env varbiable')
        sys.exit(1)
    return admin_id
