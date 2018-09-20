import os

from django import setup
from django.apps import apps
from django.conf import settings


class DjangoController(object):
    def __init__(self, settings_path):
        self.setup_django(settings_path)

    def setup_django(self, settings_path):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_path)
        setup()

    def get_or_create_user(self, update):
        user, created = apps.get_model(settings.AUTH_USER_MODEL).objects.get_or_create(
            username=update.effective_user.username
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