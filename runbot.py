# -*- coding: utf-8 -*-
import requests

from base.bot import Bot
from base.items import *


def dialog():
    authorizated = yield from authorization()
    if authorizated:
        yield 'Success, you authorizated!'
    else:
        yield 'Sorry, you are not authorizated!'

    likes_python = yield from ask_yes_or_no("Приятно познакомиться, %s. Вам нравится Питон?" % name)
    if likes_python:
        answer = yield from discuss_good_python(name)
    else:
        answer = yield from discuss_bad_python(name)


def authorization():
    url = yield 'Enter your Jira account url (company.atlassian.net)'
    username = yield 'Enter your Jira account username or email'
    token_url = 'https://id.atlassian.com/manage/api-tokens'
    token = yield f'Enter your token. You can create your token here - {token_url}'

    user_header = f'{username.text}:{token.text}'
    jira_url = f'https://{url.text}'

    response = requests.get(jira_url, headers={'user': user_header})
    if response.status_code == 200:
        return True
    return False


def ask_yes_or_no(question):
    """Спросить вопрос и дождаться ответа, содержащего «да» или «нет».

    Возвращает:
        bool
    """
    answer = yield (question, ["Да.", "Нет."])
    while not ("да" in answer.text.lower() or "нет" in answer.text.lower()):
        answer = yield HTML("Так <b>да</b> или <b>нет</b>?")
    return "да" in answer.text.lower()


def discuss_good_python(name):
    answer = yield "Мы с вами, %s, поразительно похожи! Что вам нравится в нём больше всего?" % name
    likes_article = yield from ask_yes_or_no("Ага. А как вам, кстати, статья на Хабре? Понравилась?")
    if likes_article:
        answer = yield "Чудно!"
    else:
        answer = yield "Жалко."
    return answer


def discuss_bad_python(name):
    answer = yield "Ай-яй-яй. %s, фу таким быть! Что именно вам так не нравится?" % name
    likes_article = yield from ask_yes_or_no(
        "Ваша позиция имеет право на существование. Статья "
        "на Хабре вам, надо полагать, тоже не понравилась?")
    if likes_article:
        answer = yield "Ну и ладно."
    else:
        answer = yield (
            "Что «нет»? «Нет, не понравилась» или «нет, понравилась»?",
            ["Нет, не понравилась!", "Нет, понравилась!"]
        )
        answer = yield "Спокойно, это у меня юмор такой."
    return answer


if __name__ == "__main__":
    dialog_bot = Bot(dialog)
    dialog_bot.start()
