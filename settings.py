TELEGRAM_API_KEY = 'TELEGRAM_API_KEY_HERE'

try:
    from settings_local import *
except Exception as e:
    print('Local settings can not be found.')
