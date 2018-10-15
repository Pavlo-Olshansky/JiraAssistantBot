import settings

import telegram

from datetime import datetime


def send_message(chat_id, text, reply_markup=None):
    bot = telegram.Bot(token=settings.TELEGRAM_API_KEY)
    try:
        bot.sendMessage(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup
        )
        return True
    except Exception as e:
        notify_error(e)
    return False


def notify(msg, status):
    now = datetime.now()
    text = f'[{status}] [{now}]: {msg}'
    send_message(
        chat_id=settings.FEEDBACK_RECEIVER_CHAT_ID,
        text=text
    )


def notify_error(msg):
    notify(msg, 'ERROR')


def notify_warning(msg):
    notify(msg, 'WARNING')


def debug(msg):
    if settings.DEBUG:
        print(msg)
