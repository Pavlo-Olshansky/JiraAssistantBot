import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_microservice.settings')
django.setup()

import pytest
from django.contrib.auth.models import User
from core.models import Profile


@pytest.fixture
def test_user(db):
    return User.objects.create(username='alice', first_name='Alice', last_name='Smith')


@pytest.fixture
def test_profile(test_user):
    return Profile.objects.create(user=test_user, chat_id='111111')
