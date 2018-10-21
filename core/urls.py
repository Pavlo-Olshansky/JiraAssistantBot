from django.urls import re_path

from core.views import WebhookView


app_name = 'core'
urlpatterns = [
    re_path(r'^jira_webhook$', WebhookView.as_view(), name='jira_webhook_view'),

]