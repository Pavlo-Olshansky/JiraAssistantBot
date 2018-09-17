# -*- coding: utf-8 -*-
import requests

from base.bot import Bot
from base.items import Message, Markdown, HTML


def dialog():
    authorizated = yield from authorization()
    if authorizated:
        yield 'Success, you authorizated!'
        yield ('Select an operation', [
            ['🔍 View task', '💾 Create task'],
            ['💡 Ping task', '🔧 Edit Description']]
        )
    else:
        yield 'Sorry, you are not authorizated!\n' + \
            'Try login again by typing /start.'
        yield HTML("Так <b>да</b> или <b>нет</b>?")
        yield Message("Так <b>да</b> или <b>нет</b>?")
        yield Markdown("Так <b>да</b> или <b>нет</b>?")


def authorization():
    company = yield 'Enter your Jira account name.\n' + \
        '(company from company.atlassian.net)'
    username = yield 'Enter your Jira account username or email'
    token_url = 'https://id.atlassian.com/manage/api-tokens'
    token = yield f'Enter your token.\n' + \
        f'You can create your token here - {token_url}'

    user_header = f'{username.text}:{token.text}'
    url = f'https://{company.text}.atlassian.net'

    try:
        response = requests.get(url, headers={'user': user_header})
        if response.status_code == 200:
            return True
    except Exception as e:
        print(f'Exception: {e}')
    return False


if __name__ == "__main__":
    dialog_bot = Bot(dialog)
    dialog_bot.start()
