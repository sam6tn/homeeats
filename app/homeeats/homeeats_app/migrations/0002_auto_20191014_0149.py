# Generated by Django 2.2.6 on 2019-10-14 01:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('homeeats_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cook',
            name='email',
        ),
        migrations.RemoveField(
            model_name='cook',
            name='password',
        ),
        migrations.AddField(
            model_name='cook',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='customer',
            name='last_name',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cook',
            name='last_name',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
