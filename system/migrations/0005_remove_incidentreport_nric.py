# Generated by Django 2.0.2 on 2018-04-13 14:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_auto_20180329_2137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incidentreport',
            name='nric',
        ),
    ]