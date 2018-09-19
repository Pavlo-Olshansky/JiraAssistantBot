import django
import os

from django.conf import settings


class DjangoController(object):
    def __init__(self, settings_path):
        self.setup_django(settings_path)
        # self.user = settings.AUTH_USER_MODEL.get_or_create()

    def setup_django(self, settings_path):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_path)
        django.setup()
