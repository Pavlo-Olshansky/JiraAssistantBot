# Generated by Django 2.1.1 on 2018-10-28 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='notify_on_attachment_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_attachment_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_comment_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_comment_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_comment_updeted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_sprint_closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_sprint_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_sprint_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_sprint_started',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_sprint_updeted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_task_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_task_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_task_updeted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_version_created',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_version_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_version_released',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_on_version_updeted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='notify_only_my_assignee',
            field=models.BooleanField(default=True),
        ),
    ]
