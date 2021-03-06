# Generated by Django 3.0.7 on 2020-07-08 19:37

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0012_auto_20200708_1630'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='is_liked',
        ),
        migrations.RemoveField(
            model_name='post',
            name='total_likes',
        ),
        migrations.AlterField(
            model_name='post',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2020, 7, 8, 16, 37, 44, 680664)),
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_like_date', models.DateTimeField(default=datetime.datetime(2020, 7, 8, 16, 37, 44, 681640))),
                ('post_like_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_like_post', to='network.Post')),
                ('post_like_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_like_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
