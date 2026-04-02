import pytest
from core.models import Profile
from core.services import ProfileService


@pytest.mark.django_db
class TestProfileService:
    def test_profile_creation(self):
        user = ProfileService.get_or_create('12345', 'testuser', 'Test', 'User')
        assert user.username == 'testuser'
        assert Profile.objects.filter(user=user, chat_id='12345').exists()

    def test_get_existing_profile(self):
        user = ProfileService.get_or_create('12345', 'testuser', 'Test', 'User')
        same_user = ProfileService.get_or_create('12345', 'testuser', 'Test', 'User')
        assert user.id == same_user.id

    def test_get_jira_users(self, test_user, test_profile):
        test_profile.company_name = 'acme'
        test_profile.save()
        from django.contrib.auth.models import User
        other = User.objects.create(username='bob')
        Profile.objects.create(user=other, chat_id='222', company_name='acme')
        jira_users = ProfileService.get_jira_users(test_user)
        assert other in jira_users
        assert test_user not in jira_users

    def test_update_setting(self, test_user, test_profile):
        assert test_profile.notify_on_task_created is False
        ProfileService.update_setting(test_user, 'notify_on_task_created', True)
        test_profile.refresh_from_db()
        assert test_profile.notify_on_task_created is True
