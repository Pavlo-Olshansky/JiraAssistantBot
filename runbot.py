# -*- coding: utf-8 -*-
import requests

from base.bot import Bot
from base.items import Message, Markdown, HTML

VIEW_TASK = '🔍 View task'
CREATE_TASK = '💾 Create task'
PING_TASK = '💡 Ping task'
EDIT_TASK = '🔧 Edit Description'
MENU = [
    [VIEW_TASK, CREATE_TASK],
    [PING_TASK, EDIT_TASK]
]


class Dialog(object):
    def __init__(self):
        self.authorizated = False

    def start(self):
        # authorizated = yield from authorization()
        self.authorizated = True
        if self.authorizated:
            yield Message('Success, you authorizated!')
            selection = yield ('Select an operation', MENU)
            if selection == VIEW_TASK:
                self.view_task_dialog()
            elif selection == CREATE_TASK:
                self.create_task_dialog()
            elif selection == PING_TASK:
                self.ping_task_dialog()
            elif selection == EDIT_TASK:
                self.edit_task_dialog()
        else:
            yield 'Sorry, you are not authorizated!\n' + \
                'Try login again by typing /start.'
            yield HTML("Так <b>да</b> или <b>нет</b>?")
            yield Message("Так <b>да</b> или <b>нет</b>?")
            yield Markdown("Так <b>да</b> или <b>нет</b>?")

    def view_task_dialog(self):
        pass

    def create_task_dialog(self):
        pass

    def ping_task_dialog(self):
        pass

    def edit_task_dialog(self):
        pass

    def authorization(self):
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
    dialog_bot = Bot(Dialog().start)
    dialog_bot.start()
