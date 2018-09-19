from django.db import models
from django.conf import settings


class CoreModel(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='Author',
        null=True,
        blank=True,
    )
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
