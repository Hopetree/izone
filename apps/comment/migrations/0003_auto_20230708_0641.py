# Generated by Django 2.2.28 on 2023-07-08 06:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comment', '0002_systemnotification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='systemnotification',
            name='get_p',
        ),
        migrations.AddField(
            model_name='systemnotification',
            name='get_p',
            field=models.ManyToManyField(related_name='systemnotification_recipient', to=settings.AUTH_USER_MODEL, verbose_name='收信人'),
        ),
    ]
