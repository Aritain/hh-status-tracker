import logging
import sys
import app.settings


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
app_logger = logging.getLogger('app_logger')


def get_webhooks():
    with open(f'{app.settings.RUN_DATA_PATH}/{app.settings.DISCORD_WEBHOOK_FILE}') as webhooks_file:
        discord_webhooks = webhooks_file.read().splitlines()
    return discord_webhooks


def get_tg_ids():
    with open(f'{app.settings.RUN_DATA_PATH}/{app.settings.TG_ID_FILE}') as tg_id_file:
        tg_ids = tg_id_file.read().splitlines()
    return tg_ids


def delete_tg_user(delete_candidate):
    delete_candidate = str(delete_candidate)
    tg_ids = get_tg_ids()
    tg_ids = [id for id in tg_ids if id != delete_candidate]
    with open(f'{app.settings.RUN_DATA_PATH}/{app.settings.TG_ID_FILE}', 'w') as tg_id_file:
        for user_id in tg_ids:
            tg_id_file.write(f'{user_id}\n')


def delete_discord_hook(delete_candidate):
    status = False
    webhooks = get_webhooks()
    with open(
        f'{app.settings.RUN_DATA_PATH}/{app.settings.DISCORD_WEBHOOK_FILE}',
        'w'
        ) as webhook_file:
        for webhook in webhooks:
            if delete_candidate != webhook:
                webhook_file.write(f'{webhook}\n')
            else:
                status = True
    return status


def add_user(user_id):
    with open(f'{app.settings.RUN_DATA_PATH}/{app.settings.TG_ID_FILE}', 'a') as tg_ids:
        tg_ids.write(f'{user_id}\n')
