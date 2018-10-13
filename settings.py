TELEGRAM_API_KEY = 'TELEGRAM_API_KEY_HERE'

try:
    from settings_local import * # NOQA
except Exception:
    print('Local settings can not be found.')
