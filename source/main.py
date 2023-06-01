import logging
import threading

from telegram.ext import CommandHandler
from app.bot import Bot
from app.handlers import (
    add_webhook,
    delete_webhook,
    disable_notifications,
    enable_notifications,
    get_help,
    mass_message,
    show_webhooks,
    start,
    status,
)
from app.helpers import app_logger
from app.polling import hh_polling


logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    app_logger.info('Starting Bot & Polling...')
    hh_polling_thread = threading.Thread(target=hh_polling, args=( ))
    hh_polling_thread.start()

    bot = Bot()

    bot.application.add_handler(CommandHandler("start", start))
    bot.application.add_handler(CommandHandler("help", get_help))
    bot.application.add_handler(CommandHandler("status", status))
    bot.application.add_handler(CommandHandler("add_webhook", add_webhook))
    bot.application.add_handler(CommandHandler("show_webhooks", show_webhooks))
    bot.application.add_handler(CommandHandler("delete_webhook", delete_webhook))
    bot.application.add_handler(CommandHandler("mass_message", mass_message))
    bot.application.add_handler(CommandHandler("disable_notifications", disable_notifications))
    bot.application.add_handler(CommandHandler("enable_notifications", enable_notifications))

    bot.application.run_polling()


if __name__ == "__main__":
    main()
