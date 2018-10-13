# -*- coding: utf-8 -*-
from jira import JIRA

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
        self.authorizated = yield from self.authorization()
        # self.authorizated = True

        if self.authorizated:
            selection = yield (
                'Success, you authorizated!\nSelect an operation', MENU)

            if selection.text == VIEW_TASK:
                yield from self.view_task_dialog()
            elif selection.text == CREATE_TASK:
                self.create_task_dialog()
            elif selection.text == PING_TASK:
                self.ping_task_dialog()
            elif selection.text == EDIT_TASK:
                self.edit_task_dialog()
        else:
            yield 'Sorry, you are not authorizated!\n' + \
                'Try login again by typing /start.'
            yield HTML("Так <b>да</b> или <b>нет</b>?")
            yield Message("Так <b>да</b> или <b>нет</b>?")
            yield Markdown("Так <b>да</b> или <b>нет</b>?")

    def view_task_dialog(self):
        issue_number = yield 'Enter task number'
        issue = self.jira.issue(issue_number.text)
        yield issue.fields.summary

    def create_task_dialog(self):
        pass

    def ping_task_dialog(self):
        pass

    def edit_task_dialog(self):
        pass

    def authorization(self):
        company = yield 'Enter your Jira account name.\n' + \
            '(company from company.atlassian.net)'
        login = yield 'Enter your Jira account login or email'
        token_url = 'https://id.atlassian.com/manage/api-tokens'
        token = yield f'Enter your token.\n' + \
            f'You can create your token here - {token_url}'
        url = f'https://{company.text}.atlassian.net'

        try:
            self.jira = JIRA(url, basic_auth=(login.text, token.text))
            projects = self.jira.projects()
            if projects:
                return True
        except Exception as e:
            print(f'Exception: {e}')

        return False


if __name__ == "__main__":
    dialog_bot = Bot(Dialog().start)
    dialog_bot.start()
