# Generated by Django 2.2.6 on 2020-01-24 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeeats_app', '0038_order_requested_delivery_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='requested_delivery_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]