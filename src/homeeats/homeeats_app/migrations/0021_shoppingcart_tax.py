# Generated by Django 2.2.7 on 2019-12-01 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeeats_app', '0020_address_current_customer_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcart',
            name='tax',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
    ]
