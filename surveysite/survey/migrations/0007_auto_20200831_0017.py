# Generated by Django 3.1 on 2020-08-30 22:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_auto_20200830_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responseanime',
            name='anime',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.anime'),
        ),
    ]
