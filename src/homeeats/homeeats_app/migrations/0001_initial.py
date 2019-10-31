# Generated by Django 2.2.6 on 2019-10-30 01:34

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True


    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_cook', models.BooleanField(default=False)),
                ('is_customer', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Cook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approved', models.BooleanField(default=False)),
                ('online', models.BooleanField(default=False)),
                ('kitchen_license', models.CharField(max_length=30)),
                ('phone_number', models.CharField(default='', max_length=30)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Cuisine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=30)),
                ('cooks', models.ManyToManyField(blank=True, related_name='cooks', to='homeeats_app.Cook')),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(default='', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=30)),
                ('description', models.CharField(default='', max_length=200)),
                ('ingredients', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=30), default=list, size=None)),
                ('dish_image', models.ImageField(default='', upload_to='dishes')),
                ('cook_time', models.IntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('cook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Cook')),
                ('cuisine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Cuisine')),
            ],
            options={
                'verbose_name_plural': 'Dishes',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=60)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('special_requests', models.CharField(default='', max_length=120)),
                ('status', models.CharField(choices=[('p', 'Pending'), ('c', 'Cooking'), ('o', 'Out For Delivery'), ('d', 'Delivered'), ('r', 'Rejected')], default='p', max_length=1)),
                ('cook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Cook')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Dish')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Dish_Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dish_rating', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('description', models.CharField(max_length=200)),
                ('report_flag', models.BooleanField(default=False)),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Customer')),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Dish')),
            ],
            options={
                'verbose_name': 'Dish Review',
                'verbose_name_plural': 'Dish Reviews',
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='favorites',
            field=models.ManyToManyField(blank=True, to='homeeats_app.Dish'),
        ),
        migrations.AddField(
            model_name='customer',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_name', models.CharField(default='', max_length=60)),
                ('city', models.CharField(default='', max_length=60)),
                ('state', models.CharField(default='', max_length=20)),
                ('zipcode', models.CharField(default='', max_length=20)),
                ('cook', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Cook')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='homeeats_app.Customer')),
            ],
        ),
    ]
