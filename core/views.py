import os
import json

from django import setup
from django.apps import apps
from django.conf import settings
from django.http import HttpResponse

from django.views.generic import View, DetailView
from django.views.decorators.csrf import csrf_exempt

from utils import send_message, send_gif, notify_error, debug


NOTIFY_PERMISSION_MAPPER = {
    'jira:issue_created': 'notify_on_task_created',
    'jira:issue_updated': 'notify_on_task_updeted',
    'jira:issue_deleted': 'notify_on_task_deleted',
    'comment_created': 'notify_on_comment_created',
    'comment_updated': 'notify_on_comment_updeted',
    'comment_deleted': 'notify_on_comment_deleted',
    'attachment_created': 'notify_on_attachment_created',
    'attachment_deleted': 'notify_on_attachment_deleted',
    'sprint_created': 'notify_on_sprint_created',
    'sprint_updated': 'notify_on_sprint_updeted',
    'sprint_deleted': 'notify_on_sprint_deleted',
    'sprint_started': 'notify_on_sprint_started',
    'sprint_closed': 'notify_on_sprint_closed',
    'jira:version_created': 'notify_on_version_created',
    'jira:version_updated': 'notify_on_version_updeted',
    'jira:version_deleted': 'notify_on_version_deleted',
    'jira:version_released': 'notify_on_version_released'
}


class DjangoController(object):
    def __init__(self, settings_path):
        debug('DjangoController')
        self.setup_django(settings_path)

    def setup_django(self, settings_path):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_path)
        setup()

    def get_or_create_user(self, update):
        try:
            user, created = apps.get_model(
                settings.AUTH_USER_MODEL
            ).objects.get_or_create(
                username=update.effective_user.username
            )
        except Exception as e:
            notify_error('get_or_create_user error: ' + str(e))

        debug('[{action} user {user}]'.format(
            action=created and 'Created' or 'Get',
            user=user)
        )

        if created:
            apps.get_model('core.Profile').objects.create(
                user=user,
                chat_id=update.message.chat_id
            )
        else:
            user.profile.chat_id = update.message.chat_id
            user.profile.save()

        return user

    def get_jira_users(self, user):
        return apps.get_model(
                settings.AUTH_USER_MODEL
            ).objects.filter(
                profile__company_name=user.profile.company_name
            ).exclude(
                id=user.id
            )


class WebhookView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(WebhookView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        event = data['webhookEvent']

        permission_codename = NOTIFY_PERMISSION_MAPPER.get(event, None)
        if not permission_codename:
            return HttpResponse(status=200)

        users = apps.get_model(
            settings.AUTH_USER_MODEL
        ).objects.filter(
            **{'profile__' + permission_codename: True}
        )

        # notify_only_my_assignee
        hanler_func = getattr(self, permission_codename, self.pass_func)
        hanler_func(data, users)

        return HttpResponse(status=200)


    def pass_func(self, data, users):
        pass

    def send_message_to_users(self, msg, users):
        for user in users:
            send_gif(user.profile.chat_id, 'breaking_news', msg)

    def format_msg_for_task(self, data, action):
        user = data['user']['displayName']
        task = data['issue']['key']
        description = data['issue']['fields']['description']
        summary = data['issue']['fields']['summary']
        msg = f'Task {task} {action} by {user}: ' + \
            f'{summary}\nDescription: {description}'

        return msg

    def notify_on_task_updeted(self, data, users):
        debug('[WebhookView] notify_on_task_updeted')
        msg = self.format_msg_for_task(data, 'updated')

        self.send_message_to_users(msg, users)

    def notify_on_task_created(self, data, users):
        debug('[WebhookView] notify_on_task_created')
        msg = self.format_msg_for_task(data, 'created')

        self.send_message_to_users(msg, users)

    def notify_on_task_deleted(self, data, users):
        debug('[WebhookView] notify_on_task_deleted')
        msg = self.format_msg_for_task(data, 'deleted')

        self.send_message_to_users(msg, users)

    def format_msg_for_comment(self, data, action):
        author = data['comment']['author']['displayName']
        comment_text = data['comment']['body']
        task = data['issue']['key']
        summary = data['issue']['fields']['summary']
        msg = f'Comment of user {author} {action}.\n' + \
            f'Task - {task} - {summary}:\n{comment_text}'

        return msg

    def notify_on_comment_created(self, data, users):
        debug('[WebhookView] notify_on_comment_created')
        msg = self.format_msg_for_comment(data, 'created')

        self.send_message_to_users(msg, users)

    def notify_on_comment_updeted(self, data, users):
        debug('[WebhookView] notify_on_comment_updeted')
        msg = self.format_msg_for_comment(data, 'updated')

        self.send_message_to_users(msg, users)


    def notify_on_comment_deleted(self, data, users):
        debug('[WebhookView] notify_on_comment_deleted')
        msg = self.format_msg_for_comment(data, 'deleted')

        self.send_message_to_users(msg, users)

    def format_msg_for_attachment(self, data, action):
        attachment = data['attachment']
        author = data['comment']['author']['displayName']
        content = data['attachment']['content']

        msg = f'Attachment of user {author} {action}.\n{content}'

        return msg

    def notify_on_attachment_created(self, data, users):
        debug('[WebhookView] notify_on_attachment_created')
        msg = self.format_msg_for_attachment(data, 'created')

        self.send_message_to_users(msg, users)

    def notify_on_attachment_deleted(self, data, users):
        debug('[WebhookView] notify_on_attachment_deleted')
        msg = self.format_msg_for_attachment(data, 'deleted')

        self.send_message_to_users(msg, users)

    def format_msg_for_spring(self, data, action):
        sprint_name = data['sprint']['name']

        msg = f'Sprint {sprint_name} {action}'

        return msg

    def notify_on_sprint_created(self, data, users):
        debug('[WebhookView] notify_on_sprint_created')
        msg = self.format_msg_for_spring(data, 'created')

        self.send_message_to_users(msg, users)

    def notify_on_sprint_updeted(self, data, users):
        debug('[WebhookView] notify_on_sprint_updeted')
        msg = self.format_msg_for_spring(data, 'updated')

        self.send_message_to_users(msg, users)

    def notify_on_sprint_deleted(self, data, users):
        debug('[WebhookView] notify_on_sprint_deleted')
        msg = self.format_msg_for_spring(data, 'deleted')

        self.send_message_to_users(msg, users)

    def notify_on_sprint_started(self, data, users):
        debug('[WebhookView] notify_on_sprint_started')
        msg = self.format_msg_for_spring(data, 'started')

        self.send_message_to_users(msg, users)

    def notify_on_sprint_closed(self, data, users):
        debug('[WebhookView] notify_on_sprint_closed')
        msg = self.format_msg_for_spring(data, 'closed')

        self.send_message_to_users(msg, users)

    def format_msg_for_version(self, data, action):
        version_name = data['version']['name']

        msg = f'Version {version_name} {action}'

        return msg

    def notify_on_version_created(self, data, users):
        debug('[WebhookView] notify_on_version_created')
        msg = self.format_msg_for_version(data, 'created')

        self.send_message_to_users(msg, users)

    def notify_on_version_updeted(self, data, users):
        debug('[WebhookView] notify_on_version_updeted')
        msg = self.format_msg_for_version(data, 'updated')

        self.send_message_to_users(msg, users)

    def notify_on_version_deleted(self, data, users):
        debug('[WebhookView] notify_on_version_deleted')
        msg = self.format_msg_for_version(data, 'deleted')

        self.send_message_to_users(msg, users)

    def notify_on_version_released(self, data, users):
        debug('[WebhookView] notify_on_version_released')
        msg = self.format_msg_for_version(data, 'released')

        self.send_message_to_users(msg, users)
