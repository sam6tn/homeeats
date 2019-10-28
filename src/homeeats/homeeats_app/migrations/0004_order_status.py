# Generated by Django 2.2.5 on 2019-10-28 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeeats_app', '0003_order_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('p', 'Pending'), ('c', 'Cooking'), ('o', 'Out For Delivery'), ('d', 'Delivered'), ('r', 'Rejected')], default='p', max_length=1),
        ),
    ]
