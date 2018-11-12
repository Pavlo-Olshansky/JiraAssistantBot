import settings

import collections
import collections.abc

from functools import wraps

from telegram.ext import Filters, Updater, MessageHandler
from telegram import ReplyKeyboardMarkup, ReplyMarkup, ChatAction

from base.items import Message

from core.views import DjangoController

from utils import debug, send_action


TELEGRAM_API_KEY = settings.TELEGRAM_API_KEY


class Bot(object):

    def __init__(self, generator, handlers=None, token=TELEGRAM_API_KEY):
        self.updater = Updater(token=token)
        handler = MessageHandler(
            Filters.text | Filters.command, self.handle_message
        )
        self.updater.dispatcher.add_handler(handler)
        self.handlers = collections.defaultdict(
            generator.start, handlers or {})

        self.generator = generator
        settings_path = 'django_microservice.settings'
        self.DjangoController = DjangoController(settings_path)
        self.generator.DjangoController = self.DjangoController
        self.generator.user = None

    def start(self):
        self.updater.start_polling()

    @send_action(ChatAction.TYPING)
    def handle_message(self, bot, update):
        debug('[ handle_message ]')
        self.generator.user = self.DjangoController.get_or_create_user(
            update
        )
        chat_id = update.message.chat_id
        print('passed 1')

        if update.message.text == "/start":
            self.handlers.pop(chat_id, None)
        if update.message.text == '/authorization':
            debug('[/authorization method]')
            self.generator.user = None
            self.handlers.pop(chat_id, None)

        print('passed 2')
        if chat_id not in self.handlers:
            answer = next(self.handlers[chat_id])
        else:
            print('passed 3')
            try:
                print('passed 4')
                print(str(self.handlers))
                print(update.message)
                answer = self.handlers[chat_id].send(update.message)
                print('passed 5')
            except StopIteration:
                del self.handlers[chat_id]
                print('passed 6')
                return self.handle_message(bot, update)
        self._send_answer(bot, chat_id, answer)

    def _send_answer(self, bot, chat_id, answer):
        debug("Sending answer %r to %s" % (answer, chat_id))
        if isinstance(answer, collections.abc.Iterable) and \
                not isinstance(answer, str):
            answer = list(map(self._convert_answer_part, answer))
        else:
            answer = [self._convert_answer_part(answer)]

        current_message = None
        for part in answer:
            if isinstance(part, Message):
                if current_message is not None:
                    options = dict(current_message.options)
                    options.setdefault("disable_notification", True)
                    bot.sendMessage(
                        chat_id=chat_id, text=current_message.text, **options
                    )
                current_message = part
            if isinstance(part, ReplyMarkup):
                current_message.options["reply_markup"] = part

        if current_message is not None:
            bot.sendMessage(
                chat_id=chat_id,
                text=current_message.text,
                **current_message.options
            )

    def _convert_answer_part(self, answer_part):
        if isinstance(answer_part, str):
            return Message(answer_part)
        if isinstance(answer_part, collections.abc.Iterable):
            answer_part = list(answer_part)
            if isinstance(answer_part[0], str):
                return ReplyKeyboardMarkup(
                    [answer_part], one_time_keyboard=True, resize_keyboard=True
                )
            elif isinstance(answer_part[0], collections.abc.Iterable):
                answer_part = list(map(list, answer_part))
                if isinstance(answer_part[0][0], str):
                    return ReplyKeyboardMarkup(
                        answer_part, one_time_keyboard=True, resize_keyboard=True
                    )
        return answer_part
