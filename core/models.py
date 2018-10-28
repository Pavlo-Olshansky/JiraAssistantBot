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
    jira_username_key = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )
    jira_username_display = models.CharField(
        max_length=512,
        null=True,
        blank=True
    )
    project_id = models.IntegerField(
        null=True,
        blank=True
    )
    #
    #
    #           NOTIFYING
    #
    #
    notify_only_my_assignee = models.BooleanField(
        default=True
    )
    # TASK NOTIFYING
    notify_on_task_created = models.BooleanField(
        default=False
    )
    notify_on_task_updeted = models.BooleanField(
        default=False
    )
    notify_on_task_deleted = models.BooleanField(
        default=False
    )
    # ATTACHMENT NOTIFYING
    notify_on_attachment_created = models.BooleanField(
        default=False
    )
    notify_on_attachment_deleted = models.BooleanField(
        default=False
    )
    # COMMENT NOTIFYING
    notify_on_comment_created = models.BooleanField(
        default=False
    )
    notify_on_comment_updeted = models.BooleanField(
        default=False
    )
    notify_on_comment_deleted = models.BooleanField(
        default=False
    )
    # VERSION NOTIFYING
    notify_on_version_created = models.BooleanField(
        default=False
    )
    notify_on_version_updeted = models.BooleanField(
        default=False
    )
    notify_on_version_deleted = models.BooleanField(
        default=False
    )
    notify_on_version_released = models.BooleanField(
        default=False
    )
    # SPRINT NOTIFYING
    notify_on_sprint_created = models.BooleanField(
        default=False
    )
    notify_on_sprint_updeted = models.BooleanField(
        default=False
    )
    notify_on_sprint_deleted = models.BooleanField(
        default=False
    )
    notify_on_sprint_started = models.BooleanField(
        default=False
    )
    notify_on_sprint_closed = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f'Profile with chat_id {self.chat_id}'

    class Meta:
        app_label = 'core'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
