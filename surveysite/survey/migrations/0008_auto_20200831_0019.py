# Generated by Django 3.1 on 2020-08-30 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0007_auto_20200831_0017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responseanime',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
