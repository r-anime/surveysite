# Generated by Django 3.1 on 2020-12-16 18:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0014_auto_20201216_1853'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SurveyAdditionsRemovals',
            new_name='SurveyAdditionRemoval',
        ),
    ]
