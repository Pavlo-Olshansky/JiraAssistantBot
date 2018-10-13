from django.db import models
from django.conf import settings

class CoreModel(models.Model):
    update_time = models.DateTimeField(
        'Updated',
        auto_now=True,
        null=True,
    )
    create_time = models.DateTimeField(
        'Created',
        auto_now_add=True,
        null=True,
    )

    class Meta:
        abstract = True
        ordering = 'update_time'


class Profile(CoreModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='User',
        null=True,
        blank=True,
    )
    chat_id = models.CharField(
        max_length=64,
        null=True,
        blank=True
    )
    jira_login = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )
    jira_token = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )
    company_name = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )

    def __str__(self):
        return f'Profile with chat_id {self.chat_id}'

    class Meta:
        app_label = 'core'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
