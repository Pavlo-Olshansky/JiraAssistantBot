import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from utils import send_gif


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
    'jira:version_released': 'notify_on_version_released',
}


class WebhookView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        event = data.get('webhookEvent', '')
        permission_codename = NOTIFY_PERMISSION_MAPPER.get(event)
        if not permission_codename:
            return HttpResponse(status=200)
        users = User.objects.filter(**{'profile__' + permission_codename: True})
        handler_func = getattr(self, permission_codename, self._pass)
        handler_func(data, users)
        return HttpResponse(status=200)

    def _pass(self, data, users):
        pass

    def _send_to_users(self, msg, users):
        for user in users:
            send_gif(user.profile.chat_id, 'breaking_news', msg)

    def _fmt_task(self, data, action):
        user = data['user']['displayName']
        task = data['issue']['key']
        desc = data['issue']['fields']['description']
        summary = data['issue']['fields']['summary']
        return f'Task {task} {action} by {user}: {summary}\nDescription: {desc}'

    def notify_on_task_created(self, d, u): self._send_to_users(self._fmt_task(d, 'created'), u)
    def notify_on_task_updeted(self, d, u): self._send_to_users(self._fmt_task(d, 'updated'), u)
    def notify_on_task_deleted(self, d, u): self._send_to_users(self._fmt_task(d, 'deleted'), u)

    def _fmt_comment(self, data, action):
        author = data['comment']['author']['displayName']
        body = data['comment']['body']
        task = data['issue']['key']
        summary = data['issue']['fields']['summary']
        return f'Comment of user {author} {action}.\nTask - {task} - {summary}:\n{body}'

    def notify_on_comment_created(self, d, u): self._send_to_users(self._fmt_comment(d, 'created'), u)
    def notify_on_comment_updeted(self, d, u): self._send_to_users(self._fmt_comment(d, 'updated'), u)
    def notify_on_comment_deleted(self, d, u): self._send_to_users(self._fmt_comment(d, 'deleted'), u)

    def _fmt_attachment(self, data, action):
        author = data['comment']['author']['displayName']
        content = data['attachment']['content']
        return f'Attachment of user {author} {action}.\n{content}'

    def notify_on_attachment_created(self, d, u): self._send_to_users(self._fmt_attachment(d, 'created'), u)
    def notify_on_attachment_deleted(self, d, u): self._send_to_users(self._fmt_attachment(d, 'deleted'), u)

    def _fmt_sprint(self, data, action):
        return f'Sprint {data["sprint"]["name"]} {action}'

    def notify_on_sprint_created(self, d, u): self._send_to_users(self._fmt_sprint(d, 'created'), u)
    def notify_on_sprint_updeted(self, d, u): self._send_to_users(self._fmt_sprint(d, 'updated'), u)
    def notify_on_sprint_deleted(self, d, u): self._send_to_users(self._fmt_sprint(d, 'deleted'), u)
    def notify_on_sprint_started(self, d, u): self._send_to_users(self._fmt_sprint(d, 'started'), u)
    def notify_on_sprint_closed(self, d, u): self._send_to_users(self._fmt_sprint(d, 'closed'), u)

    def _fmt_version(self, data, action):
        return f'Version {data["version"]["name"]} {action}'

    def notify_on_version_created(self, d, u): self._send_to_users(self._fmt_version(d, 'created'), u)
    def notify_on_version_updeted(self, d, u): self._send_to_users(self._fmt_version(d, 'updated'), u)
    def notify_on_version_deleted(self, d, u): self._send_to_users(self._fmt_version(d, 'deleted'), u)
    def notify_on_version_released(self, d, u): self._send_to_users(self._fmt_version(d, 'released'), u)
