# Generated by Django 3.1 on 2020-08-28 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_auto_20200828_0251'),
    ]

    operations = [
        migrations.RenameField(
            model_name='survey',
            old_name='season',
            new_name='year_season',
        ),
    ]
