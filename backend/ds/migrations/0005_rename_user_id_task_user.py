# Generated by Django 4.1 on 2022-09-03 10:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ds', '0004_page_alter_task_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='user_id',
            new_name='user',
        ),
    ]
