# Generated by Django 2.2.7 on 2020-03-26 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeeats_app', '0043_auto_20200326_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='dish_image',
            field=models.ImageField(blank=True, default='', null=True, upload_to='dishes'),
        ),
    ]
