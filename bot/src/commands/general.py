import shelve
import socket

import telegram
import psutil

from monitor import daemon

# Stores the latest message the user is seeing
user_message_dict = shelve.open('user_message_dict')


def handle_start(update, context):
    daemon.report_lock.acquire()
    report = daemon.report
    daemon.report_lock.release()

    message = context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=report,
                                       parse_mode='HTML')
    user_message_dict[str(update.effective_chat.id)] = str(message.message_id)


def handle_unsub(update, context):
    del user_message_dict[str(update.effective_chat.id)]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="unsubscribed to update")
