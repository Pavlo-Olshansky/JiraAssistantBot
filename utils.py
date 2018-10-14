import settings

import telegram


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
        print(e)
    return False
