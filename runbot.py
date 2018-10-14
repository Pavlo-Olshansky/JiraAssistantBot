# -*- coding: utf-8 -*-
import settings
import telegram

from jira import JIRA

from base.bot import Bot
from base.items import Message, Markdown, HTML
from base.menu import (VIEW_TASK, CREATE_TASK, PING_TASK,
    EDIT_TASK, AUTHORIZATION, FEEDBACK, MENU, YES, NO, YES_NO_QUESTION,
    CANCEL)

from core.views import DjangoController

from utils import send_message, notify_error, debug


class Dialog(object):
    def __init__(self):
        self.authorizated = False
        self.answer = None

    def start(self):
        debug('[Start Dialog]')
        self.authorizated = self.authorization()
        if not self.authorizated:
            self.authorizated = yield from self.get_creditails()

        if self.authorizated:
            selection = yield (self.answer or 'Select an operation', MENU)
            self.answer = None

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
        task_number = yield from self.get_task_number()
        try:
            issue = self.jira.issue(task_number)
        except Exception as e:
            notify_warning(e)
            self.answer = f'Sorry, task {task_number} does not exist.'
            return

        labels = str(' '.join(issue.fields.labels))
        url = self.get_task_url(task_number)
        task_details = '`{summary}`{labels}\n\n {description}\n\n{url}'.format(
            summary=issue.fields.summary,
            labels='\nLabels: `' + labels + '`',
            description=issue.fields.description,
            url=url
        )
        self.answer = Markdown(task_details)

    def create_task_dialog(self):
        project = self.get_user_project()

        confirmation = f'Create new task for project `{project.name}` ?'
        confirm_creation = yield (Markdown(confirmation), YES_NO_QUESTION)

        if confirm_creation.text != YES:
            return
        task_summary = yield ('Enter task title:')
        task_description = yield ('Enter task description:')

        try:
            new_issue = self.jira.create_issue(
                project={'id': project.id},
                summary=task_summary.text,
                description=task_description.text
            )
        except Exception as e:
            notify_error(e)
            self.answer = 'Error. Task is not created for task'
            return

        task_url = self.get_task_url(new_issue.key)
        self.answer = f'Task {new_issue.key} created.\n{task_url}'

    def ping_task_dialog(self):
        users = self.DjangoController.get_jira_users(self.user)
        if not users:
            self.answer = 'Sorry, there is no your team in Jira Bot.' + \
                'Share @JiraAssistant_Bot with your team and ping them !'
            return

        users_menu = [[str(user.profile.jira_username_display) + ' (' + \
                str(user.profile.jira_username_key) + ')'
            ] for user in users]

        users_menu.append([CANCEL])

        user = None
        selected_user = yield ('Select a user.', users_menu)
        jira_username_key_selected = selected_user.text.split('(')[-1][:-1]
        user = users.filter(
            profile__jira_username_key=jira_username_key_selected
        ).first()

        while not (user or selected_user.text == CANCEL):
            selected_user = yield ('Please, choose an existing user.', users_menu)
            jira_username_key_selected = selected_user.text.split('(')[-1][:-1]
            user = users.filter(
                profile__jira_username_key=jira_username_key_selected
            ).first()
        if selected_user.text == CANCEL:
            return

        task_number = yield('Enter task number to ping.')
        ping_success = self.ping_user(
            user=user,
            task_number=task_number.text
        )
        if ping_success:
            self.answer = f'Ping user {selected_user.text} for task ' + \
                f'{task_number.text} success!'
        else:
            self.answer = 'Ping Failure.' + \
                'Something went wrong, please try again.'

    def edit_task_dialog(self):
        task_number = yield from self.get_task_number()
        try:
            issue = self.jira.issue(task_number)
        except Exception as e:
            notify_error(e)
            self.answer = f'Sorry, task {task_number} does not exist.'
            return

        msg = f'Edit task {task_number} ? (`{issue.fields.summary}`)'
        confirm_edit = yield (Markdown(msg), YES_NO_QUESTION)
        if confirm_edit.text != YES:
            return

        edit_question = 'What you want to edit ?'
        TITLE = 'Title'
        DESCRIPTION = 'Description'
        edit_option = [TITLE, DESCRIPTION, CANCEL]
        to_edit = yield (edit_question, edit_option)
        while not (to_edit.text in edit_option):
            to_edit = yield ('Please, choose a valid option', edit_option)

        if to_edit.text == TITLE:
            response = yield from self.edit_task_title(issue)
        elif to_edit.text == DESCRIPTION:
            response = yield from self.edit_task_description(issue)
        elif to_edit.text == CANCEL:
            return
        else:
            return
        return response

    def change_credentials_dialog(self):
        project = self.get_user_project()
        msg = 'Current credentials:\n' + \
            f'Company: `{self.user.profile.company_name}`\n' + \
            f'Login: `{self.user.profile.jira_login}`\n' + \
            f'Token: `{self.user.profile.jira_token}`\n' + \
            f'Project: `{project.name}`\n\n' + \
            'Are you want to change your credentials ?'
        answer = yield (Markdown(msg), ['Yes', 'No'])

        if answer.text == 'Yes':
            self.authorizated = yield from self.get_creditails()

    def feedback_dialog(self):
        feedback = yield ('Please, write a feedback:')

        message_is_sent = send_message(
            chat_id=settings.FEEDBACK_RECEIVER_CHAT_ID,
            text=f'Йо чувааак, тут фідбек тобі пишуть кароч:\n{feedback.text}'
        )
        if message_is_sent:
            self.answer = 'Thanks, you`re the best 👍\n' + \
                'We will consider your wishes.'
        else:
            self.answer = 'Sorry, an error occured.'

    def authorization(self):
        debug('[Authorization]')
        if self.user and self.user.profile.jira_login and \
                self.user.profile.jira_token:
            return self.check_jira_connection()

        return False

    def check_jira_connection(self):
        debug('[Checking jira connection]')

        try:
            url = f'https://{self.user.profile.company_name}.atlassian.net'
            self.jira = JIRA(url, basic_auth=(
                self.user.profile.jira_login, self.user.profile.jira_token))
            users = self.jira.search_users(self.user.profile.jira_login)
            if users:
                self.user.profile.jira_username_key = users[0].key
                self.user.profile.jira_username_display = users[0].displayName
                return True
        except Exception as e:
            notify_error(e)

        return False

    def get_creditails(self):
        debug(f'[Grtting creditails for {self.user}]')
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

        is_connected = self.check_jira_connection()
        if is_connected:
            self.user.profile.project_id = self.jira.projects()[0].id
            self.user.profile.save()
            username = ', ' + self.user.profile.jira_username_display or ''
            self.answer = f'Welcome{username}! You are loggined successfully.'
            return True

        return False

    def ping_user(self, user, task_number):
        url = f'https://{self.user.profile.company_name}.' + \
            'atlassian.net/browse/{task_number}'
        msg = 'User {user} ping you about the task {task} - {url}'.format(
            user=self.user.profile.jira_username_display,
            task=task_number,
            url=url
        )

        button_list = []
        reply_markup = telegram.InlineKeyboardMarkup([
            [telegram.InlineKeyboardButton(
                '🔗 Open in browser',
                url=url)],
            button_list])

        message_is_sent = send_message(
            chat_id=user.profile.chat_id,
            text=msg,
            reply_markup=reply_markup
        )
        return message_is_sent

    def get_task_url(self, task_number):
        company = self.user.profile.company_name
        url = f'https://{company}.atlassian.net/browse/{task_number}'
        return url

    def get_user_project(self):
        return self.jira.project(self.user.profile.project_id)

    def get_task_number(self):
        project = self.get_user_project()
        number = yield Markdown(f'Enter task number:\n`{project.key}-`')
        task_number = f'{project.key}-{number.text}'
        return task_number

    def edit_task_title(self, issue):
        prev_title_question = 'What title do you want to set ?\n' + \
            f'Previous title - `{issue.fields.summary}`.'
        new_title = yield Markdown(prev_title_question)
        try:
            issue.update(summary=new_title.text)
        except Exception as e:
            notify_error(e)
            self.answer = f'Error. Title for task {issue.key} ' + \
                'is not updated.'
            return
        self.answer = f'Title for task {issue.key} updated !'

    def edit_task_description(self, issue):
        prev_description_question = 'What description do you want to set ?\n' + \
            f'Previous description - `{issue.fields.description}`.'
        new_description = yield Markdown(prev_description_question)
        try:
            issue.update(description=new_description.text)
        except Exception as e:
            notify_error(e)
            self.answer = 'Error. Description for task ' + \
                f'{issue.key} is not updated.'
            return
        self.answer = f'Description for task {issue.key} updated !'


if __name__ == "__main__":
    dialog_instance = Dialog()
    dialog_bot = Bot(dialog_instance)
    dialog_bot.start()
