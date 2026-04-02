from decouple import config, Csv

TELEGRAM_API_KEY = config('TELEGRAM_API_KEY')
FEEDBACK_RECEIVER_CHAT_ID = config('FEEDBACK_RECEIVER_CHAT_ID', default='')

DB_NAME = config('DB_NAME', default='jira_bot')
DB_USER = config('DB_USER', default='postgres')
DB_PASSWORD = config('DB_PASSWORD', default='postgres')
DB_HOST = config('DB_HOST', default='localhost')
DB_PORT = config('DB_PORT', default='5432')

DEBUG = config('DEBUG', default=True, cast=bool)
