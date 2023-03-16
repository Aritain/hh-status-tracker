from telegram import Update, error
from telegram.ext import ContextTypes
from app.bot import Bot
from app.helpers import (
    delete_discord_hook,
    delete_tg_user,
    get_tg_ids,
    get_webhooks
)
from app.settings import (
    DISCORD_WEBHOOK_FILE,
    get_bot_admin,
    TG_ID_FILE,
    RUN_DATA_PATH
)
from app.polling import get_server_status


HELP_MESSAGE = (
    'Commands usage:\n\n'
    '/status - shows the current server status\n'
    '/add_webhook - add discord webhook, place webhook after command separated by whitespace\n'
    '/show_webhooks - show the list of discord webhooks you added\n'
    '/delete_webhook - deletes discord webhook, place webhook after command separated'
    ' by whitespace\n'
    '😘😘😘'
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_ids = get_tg_ids()
    if str(update.message.from_user.id) in tg_ids:
        return
    with open(f'{RUN_DATA_PATH}/{TG_ID_FILE}', 'a') as tg_ids:
        tg_ids.write(f'{update.message.from_user.id}\n')
    await update.message.reply_text("Bot successfully started 😍")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    server_status = get_server_status()
    if "up" in server_status:
        message_text = "The server is up 😍"
    else:
        message_text = "The server is down 😕"
    await update.message.reply_text(message_text)


async def add_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(update.message.text.split()) == 1:
        await update.message.reply_text(HELP_MESSAGE)
        return

    webhook = update.message.text.split()[1]
    if "https://discord.com/api/webhooks/" not in webhook:
        await update.message.reply_text("Wrong discord webhook format 🙄")
        return

    new_entry = str(update.message.from_user.id) + ";" + webhook

    webhooks = get_webhooks()
    if new_entry in webhooks:
        await update.message.reply_text("You already added this webhook 🙄")
    else:
        with open(f'{RUN_DATA_PATH}/{DISCORD_WEBHOOK_FILE}', 'a') as webhook_file:
            webhook_file.write(f'{new_entry}\n')
        await update.message.reply_text("Webhook successfully added 😍")


async def show_webhooks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    webhooks = get_webhooks()

    user_webhooks = []
    for webhook in webhooks:
        username, hook = webhook.split(';')
        if username == str(update.message.from_user.id):
            user_webhooks.append(hook)

    if len(user_webhooks) != 0:
        message_text = "The list of webhooks added by you:\n\n"
        message_text += '\n\n'.join(user_webhooks)
    else:
        message_text = "There are no webhooks added by you 😭"

    await update.message.reply_text(message_text)


async def delete_webhook(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(update.message.text.split()) == 1:
        await update.message.reply_text(HELP_MESSAGE)
        return

    delete_candidate = str(update.message.from_user.id) + ";" + update.message.text.split()[1]
    delete_status = delete_discord_hook(delete_candidate)

    if delete_status:
        await update.message.reply_text("Webhook successfully deleted 😭")
    else:
        await update.message.reply_text("Failed to find provided webhook 🤔")


async def mass_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = Bot()
    if update.message.from_user.id == get_bot_admin():
        tg_ids = get_tg_ids()
        message = ' '.join(update.message.text.split()[1:])

        for user_id in tg_ids:
            try:
                await bot.send_message(chat_id = user_id, text = message)
            except error.Forbidden:
                app_logger.warn(f'tg user {user_id} blocked the bot, deleting...')
                delete_tg_user(delete_candidate = user_id)


async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MESSAGE)
