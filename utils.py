import settings

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
    if ERROR_RECEIVER_CHAT_ID:
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
