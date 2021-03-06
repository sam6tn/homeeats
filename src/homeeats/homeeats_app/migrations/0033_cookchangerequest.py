# Generated by Django 2.2.6 on 2019-12-05 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeeats_app', '0032_cook_government_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CookChangeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kitchen_license', models.CharField(max_length=30)),
                ('phone_number', models.CharField(default='', max_length=30)),
                ('street_name', models.CharField(default='', max_length=60)),
                ('city', models.CharField(default='', max_length=60)),
                ('state', models.CharField(default='', max_length=20)),
                ('zipcode', models.CharField(default='', max_length=20)),
            ],
        ),
    ]
