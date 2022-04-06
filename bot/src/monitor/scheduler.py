import logging

import telegram
from telegram import ext

from commands.general import user_message_dict
from monitor import daemon


def scheduler(job_queue: ext.JobQueue):
    job_queue.run_repeating(callback=broadcast, interval=30)


def broadcast(context):
    logging.info(f'broadcasting to {len(user_message_dict)} users')

    daemon.report_lock.acquire()
    _report = daemon.report
    daemon.report_lock.release()

    for chat_id, message_id in user_message_dict.items():
        try:
            context.bot.edit_message_text(chat_id=int(chat_id),
                                          message_id=int(message_id),
                                          text=_report,
                                          parse_mode=telegram.ParseMode.HTML)
        except telegram.error.BadRequest as err:
            if not err.message.startswith('Message is not modified:'):
                logging.error(f'update_user_message_failed_with_err_{err}')
    logging.info("broadcast finish")
