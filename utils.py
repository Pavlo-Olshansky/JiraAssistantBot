import settings
from random import randint

import telegram

from functools import wraps

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


STICKERS_FILE_ID_MAPPER = {
    'ok': [
        'CAADAgADGQADyIsGAAFl6KYZBflVyQI', # Abraham Lincoln approves
        'CAADAgADEgADyIsGAAE-gRk5Wrs8NwI', # Julius Caesar approves
        'CAADAgADPQADyIsGAAER4mZIkRHRsgI'  # Brus Lee approves
    ]
}

GIFS_FILE_ID_MAPPER = {
    'thank you': 'CgADAgADKgMAAkArIEh3RhMT3wABil0C'
}


def send_sticker(chat_id, sticker_name):
    bot = telegram.Bot(token=settings.TELEGRAM_API_KEY)

    sticker_set = STICKERS_FILE_ID_MAPPER.get(sticker_name)

    try:
        random_sticker_index = randint(0, len(sticker_set) - 1)
        sticker = sticker_set[random_sticker_index]

        stickers = bot.sendSticker(chat_id=chat_id, sticker=sticker)
        return True
    except Exception as e:
        notify_error(e)
    return False


def send_gif(chat_id, gif_name, caption=''):
    debug('[send_gif]')
    gif_file_id = GIFS_FILE_ID_MAPPER.get(gif_name)

    send_document(chat_id, gif_file_id, caption=caption)


def send_document(chat_id, document_file_id, caption):
    try:
        bot = telegram.Bot(token=settings.TELEGRAM_API_KEY)
        bot.sendDocument(
            chat_id=chat_id,
            document=document_file_id,
            caption=caption
        )
    except Exception as e:
        notify_error(e)


def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            _self, bot, update = args
            bot.sendChatAction(chat_id=update.message.chat_id, action=action)
            func(_self, bot, update, **kwargs)
        return command_func

    return decorator


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def notify(msg, status):
    now = datetime.now()
    text = f'[{status}] [{now}]: {msg}'
    if settings.ERROR_RECEIVER_CHAT_ID:
        send_message(
            chat_id=settings.ERROR_RECEIVER_CHAT_ID,
            text=text
        )
    else:
        print(text)


def notify_error(msg):
    notify(msg, 'ERROR')


def notify_warning(msg):
    notify(msg, 'WARNING')


def debug(msg):
    if settings.DEBUG:
        print(msg)
