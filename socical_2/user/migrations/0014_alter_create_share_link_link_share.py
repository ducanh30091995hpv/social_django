# Generated by Django 3.2.8 on 2021-10-12 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_create_share_link_share_link_share_link_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='create_share_link',
            name='link_share',
            field=models.TextField(unique=True),
        ),
    ]