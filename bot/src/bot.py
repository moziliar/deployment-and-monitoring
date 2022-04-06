import logging
import os

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from commands.general import (
    handle_start,
    handle_unsub
)
from monitor.scheduler import scheduler
from monitor.daemon import (
    MonitorDaemon,
)


def main():
    # Set use_context=True to use the new context based callbacks
    updater = Updater(token=os.getenv('BOT_TOKEN'), use_context=True)

    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler('start', handle_start))
    dispatcher.add_handler(CommandHandler('unsub', handle_unsub))

    # Start the Bot
    updater.start_polling()

    logging.info('Bot started')

    # Start machine monitor daemon
    MonitorDaemon().start()

    scheduler(updater.job_queue)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logging.info('Bot is starting')
    load_dotenv()
    main()
