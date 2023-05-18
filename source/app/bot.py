import app.helpers

from telegram import error
from telegram.ext import Application
from app.settings import get_token


# Dedicated class so it's available within all app modules
class Bot:
    def __init__(self):
        self.application = Application.builder().token(get_token()).build()

    async def send_message(self, chat_id: int, text: str):
        try:
            app.helpers.app_logger.info(f'Attempting to send a message to {chat_id}')
            await self.application.bot.send_message(chat_id=chat_id, text=text)
        except (error.Forbidden, error.BadRequest):
            app.helpers.app_logger.warn(f'Telegam user {chat_id} blocked the bot, deleting...')
            app.helpers.delete_tg_user(delete_candidate = user_id)
