from telegram.ext import Application
from app.settings import get_token


# Dedicated class so it's available within all app modules
class Bot:
    def __init__(self):
        self.application = Application.builder().token(get_token()).build()

    async def send_message(self, chat_id: int, text: str):
        await self.application.bot.send_message(chat_id=chat_id, text=text)
