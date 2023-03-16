from discord_webhook import DiscordWebhook
from telegram import error
from app.bot import Bot
from app.helpers import (
    app_logger,
    delete_discord_hook,
    delete_tg_user,
    get_tg_ids,
    get_webhooks
)
from app.settings import FORUM_LINK


def prepare_status_msg(message_data):
    if "up" in message_data:
        return "The server went up 😍"
    return "The server went down 😱"


def prepare_topic_msg(message_data):
    return ('Got new announcement topic 👀\n\n'
            f'{message_data[0]}\n'
            f'{FORUM_LINK}{message_data[2]}'
    )


async def message_tg(message):
    bot = Bot()
    tg_ids = get_tg_ids()


    for user_id in tg_ids:
        try:
            await bot.send_message(chat_id = user_id, text = message)
        except error.Forbidden:
            app_logger.warn(f'tg user {user_id} blocked the bot, deleting...')
            delete_tg_user(delete_candidate = user_id)


async def message_discord(message):
    discord_webhooks = get_webhooks()
    bot = Bot()

    for elem in discord_webhooks:
        '''
        Since webhook file has the following structure:
        <telegram user id>;<discord webhook>
        We need to extract webhooks only out of that
        '''
        url = elem.split(';')[1]
        webhook = DiscordWebhook(
            url=url, content=message)
        result = webhook.execute()
        if '40' in str(result):
            app_logger.warn(f'Failed to send message for webhook {url}, deleting...')
            delete_discord_hook(delete_candidate = elem)
            delete_message = f'Your webhook {url} was deleted 😭'
            await bot.send_message(chat_id = elem.split(';')[0], text = delete_message)


async def mass_message(message_data):
    # Status comes in str and topic comes in a list
    if isinstance(message_data, str):
        message = prepare_status_msg(message_data)
    else:
        message = prepare_topic_msg(message_data)

    await message_tg(message)
    await message_discord(message)
