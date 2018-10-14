# Generated by Django 2.1.1 on 2018-10-14 15:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created')),
                ('chat_id', models.CharField(blank=True, max_length=64, null=True)),
                ('jira_login', models.CharField(blank=True, max_length=512, null=True)),
                ('jira_token', models.CharField(blank=True, max_length=512, null=True)),
                ('company_name', models.CharField(blank=True, max_length=512, null=True)),
                ('jira_username_key', models.CharField(blank=True, max_length=512, null=True)),
                ('jira_username_display', models.CharField(blank=True, max_length=512, null=True)),
                ('project_id', models.IntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
    ]
