# Generated by Django 2.2.7 on 2019-12-07 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeeats_app', '0034_cookchangerequest_cook'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(default='', max_length=60),
        ),
        migrations.AddField(
            model_name='order',
            name='state',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='street_name',
            field=models.CharField(default='', max_length=60),
        ),
        migrations.AddField(
            model_name='order',
            name='zipcode',
            field=models.CharField(default='', max_length=20),
        ),
    ]
