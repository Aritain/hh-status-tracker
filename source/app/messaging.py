import asyncio

from discord_webhook import DiscordWebhook
from .bot import Bot
from .helpers import (
    app_logger,
    delete_discord_hook,
    delete_tg_user,
    get_tg_ids,
    get_webhooks
)
from .settings import FORUM_LINK


def prepare_status_msg(message_data):
    if "up" in message_data:
        return "The server went up 😍"
    return "The server went down 😱"


def prepare_topic_msg(message_data):
    return ('Got new announcement topic 👀\n\n'
            f'{message_data[0]}\n'
            f'{FORUM_LINK}{message_data[2]}'
    )


async def message_tg(message, bot, user_id):
    await bot.send_message(chat_id = user_id, text = message)


async def message_discord(message, bot, discord_webhook):
    '''
    Since webhook file has the following structure:
    <telegram user id>;<discord webhook>
    We need to extract webhooks only out of that
    '''
    url = discord_webhook.split(';')[1]
    webhook = DiscordWebhook(
        url=url, content=message)
    result = webhook.execute()
    if '40' in str(result):
        app_logger.warn(f'Failed to send message for webhook {url}, deleting...')
        delete_discord_hook(delete_candidate = discord_webhook)
        delete_message = f'Your webhook {url} got deleted 😭'
        await bot.send_message(chat_id = discord_webhook.split(';')[0], text = delete_message)


async def mass_message(message_data):
    # Status comes in str and topic comes in a list
    if isinstance(message_data, str):
        message = prepare_status_msg(message_data)
    else:
        message = prepare_topic_msg(message_data)

    discord_webhooks = get_webhooks()
    tg_ids = get_tg_ids()
    bot = Bot()
    messaging_tasks = []

    for tg_id in tg_ids:
        messaging_tasks.append(asyncio.create_task(message_tg(message, bot, tg_id)))
    for discord_webhook in discord_webhooks:
        messaging_tasks.append(asyncio.create_task(message_discord(message, bot, discord_webhook)))

    await asyncio.gather(*messaging_tasks)
