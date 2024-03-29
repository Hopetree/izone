# Generated by Django 2.2.28 on 2023-07-09 12:37

from django.db import migrations
import imagekit.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0002_auto_20230423_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ouser',
            name='avatar',
            field=imagekit.models.fields.ProcessedImageField(default='avatar/default/default.png', upload_to='avatar/upload/%Y/%m/%d/%H-%M-%S', verbose_name='头像'),
        ),
    ]
