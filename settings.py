TELEGRAM_API_KEY = 'TELEGRAM_API_KEY_HERE'
FEEDBACK_RECEIVER_CHAT_ID = 'FEEDBACK_RECEIVER_CHAT_ID_HERE'
DEBUG = False

try:
    from settings_local import * # NOQA
except Exception:
    print('Local settings can not be found.')
