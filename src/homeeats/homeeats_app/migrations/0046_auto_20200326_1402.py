# Generated by Django 2.2.7 on 2020-03-26 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeeats_app', '0045_auto_20200326_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='dish_image',
            field=models.ImageField(default='', upload_to='dishes'),
        ),
    ]
