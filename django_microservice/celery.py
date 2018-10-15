import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_microservice.settings')

app = Celery('django_microservice')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
