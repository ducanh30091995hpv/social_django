# Generated by Django 3.2.7 on 2021-10-20 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0018_auto_20211016_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_post',
            name='tag',
            field=models.TextField(default='', null=True),
        ),
    ]
