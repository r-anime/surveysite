# Generated by Django 3.1 on 2021-06-06 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_missinganime'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='missinganime',
            options={'verbose_name_plural': 'missing anime'},
        ),
        migrations.AddField(
            model_name='missinganime',
            name='name',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='missinganime',
            name='description',
            field=models.TextField(blank=True, max_length=128),
        ),
    ]
