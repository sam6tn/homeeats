# Generated by Django 2.2.7 on 2019-12-02 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeeats_app', '0022_order_pending_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='estimated_arrival_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
