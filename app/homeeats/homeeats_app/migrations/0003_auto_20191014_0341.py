# Generated by Django 2.2.6 on 2019-10-14 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeeats_app', '0002_auto_20191014_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='last_name',
            field=models.CharField(max_length=30),
        ),
    ]
