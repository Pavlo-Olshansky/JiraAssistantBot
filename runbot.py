# -*- coding: utf-8 -*-
from jira import JIRA

from base.bot import Bot
from base.items import Message, Markdown, HTML
from base.menu import (VIEW_TASK, CREATE_TASK, PING_TASK,
    EDIT_TASK, AUTHORIZATION, FEEDBACK, MENU)

from core.views import DjangoController


class Dialog(object):
    def __init__(self):
        self.authorizated = False
        self.answer = None

    def start(self):
        print('[Start Dialog]')
        self.authorizated = self.authorization()
        print('self.authorizated: ', self.authorizated)
        if not self.authorizated:
            self.authorizated = yield from self.get_creditails()

        if self.authorizated:
            selection = yield (self.answer or 'Select an operation', MENU)
            self.answer = None
            print('selection: ', selection)

            if selection.text == VIEW_TASK:
                yield from self.view_task_dialog()
            elif selection.text == CREATE_TASK:
                yield from self.create_task_dialog()
            elif selection.text == PING_TASK:
                yield from self.ping_task_dialog()
            elif selection.text == EDIT_TASK:
                yield from self.edit_task_dialog()
            elif selection.text == AUTHORIZATION:
                yield from self.change_credentials_dialog()
            elif selection.text == FEEDBACK:
                yield from self.feedback_dialog()
        else:
            yield 'Sorry, you are not authorizated!\n' + \
                'Try login again by typing /authorization.'

    def view_task_dialog(self):
        issue_number = yield 'Enter task number'
        issue = self.jira.issue(issue_number.text)
        self.answer = issue.fields.summary

    def create_task_dialog(self):
        pass

    def ping_task_dialog(self):
        pass

    def edit_task_dialog(self):
        pass

    def change_credentials_dialog(self):
        msg = 'Current credentials:\n' + \
            f'Company: `{self.user.profile.company_name}`\n' + \
            f'Login: `{self.user.profile.jira_login}`\n' + \
            f'Token: `{self.user.profile.jira_token}`\n\n' + \
            'Are you want to change your credentials ?'
        print('msg: ', msg)
        answer = yield (Markdown(msg), ['Yes', 'No'])

        if answer.text == 'Yes':
            self.authorizated = yield from self.get_creditails()

    def authorization(self):
        print('[Authorization]')
        if self.user and self.user.profile.jira_login and \
                self.user.profile.jira_token:
            print('user: ', self.user, self.user.profile.jira_login, self.user.profile.jira_token)
            return self.check_jira_connection()

        return False

    def check_jira_connection(self):
        print('[Checking jira connection]')
        try:
            url = f'https://{self.user.profile.company_name}.atlassian.net'
            self.jira = JIRA(url, basic_auth=(
                self.user.profile.jira_login, self.user.profile.jira_token)
            )
            projects = self.jira.projects()
            if projects:
                return True
        except Exception as e:
            print(f'Exception: {e}')
        
        return False

    def get_creditails(self):
        print(f'[Grtting creditails for {self.user}]')
        company = yield 'Enter your Jira account name.\n' + \
            '(company from company.atlassian.net)'
        login = yield 'Enter your Jira account login or email'
        token_url = 'https://id.atlassian.com/manage/api-tokens'
        token = yield f'Enter your token.\n' + \
            f'You can create your token here - {token_url}'
        url = f'https://{company.text}.atlassian.net'
        self.user.profile.company_name = company.text
        self.user.profile.jira_login = login.text
        self.user.profile.jira_token = token.text
        self.user.profile.save()

        try:
            self.jira = JIRA(url, basic_auth=(login.text, token.text))
            print(str(self.jira), '___-_-____')
            projects = self.jira.projects()
            print('projects: ', projects)
            if projects:
                print('return True from get_creditails')
                self.answer = 'You are loggined successfully!'
                return True
        except Exception as e:
            print(f'Exception: {e}')

        print('return False from get_creditails')
        return False


if __name__ == "__main__":
    dialog_instance = Dialog()
    dialog_bot = Bot(dialog_instance)
    dialog_bot.start()
