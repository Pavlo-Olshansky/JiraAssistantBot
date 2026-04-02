from __future__ import annotations

from django.contrib.auth.models import User
from django.db.models import QuerySet

from core.models import Profile


class ProfileService:
    @staticmethod
    def get_or_create(chat_id: str, username: str, first_name: str = '', last_name: str = '') -> User:
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.first_name = first_name
            user.last_name = last_name or first_name
            user.save()
            Profile.objects.create(user=user, chat_id=chat_id)
        else:
            Profile.objects.filter(user=user).update(chat_id=chat_id)
        return user

    @staticmethod
    def get_profile(user: User) -> Profile:
        return Profile.objects.get(user=user)

    @staticmethod
    def get_jira_users(user: User) -> QuerySet:
        return User.objects.filter(
            profile__company_name=user.profile.company_name
        ).exclude(id=user.id)

    @staticmethod
    def update_setting(user: User, field: str, value) -> None:
        Profile.objects.filter(user=user).update(**{field: value})
