# Generated by Django 3.1 on 2021-03-23 22:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_auto_20210119_2204'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='survey',
            options={'ordering': ['year', '-season', 'is_preseason']},
        ),
    ]
