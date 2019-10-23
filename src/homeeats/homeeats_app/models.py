from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from .managers import CustomUserManager
from django.utils.translation import ugettext_lazy as _


# class CustomUser(AbstractUser):
#  username = None
#  email = models.EmailField(_('email_address'), unique=True)

#  USERNAME_FIELD = 'email'
#  REQUIRED_FIELDS = []
#  objects = CustomUserManager()

#  def __str__(self):
#    return self.email

'''
Columns in the cook database table
'''
class Cook(models.Model):
  approved = models.BooleanField(default=False)
  online = models.BooleanField(default=False)
  kitchen_license = models.CharField(max_length=30)
  phone_number = models.CharField(max_length=30, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE)

class Cuisine(models.Model):
  type = models.CharField(default="", max_length=30)
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)

class Dish(models.Model):
  title = models.CharField(default="", max_length=30)
  cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE)
  description = models.CharField(default="", max_length=200)
  ingredients = ArrayField(models.CharField(max_length=30, blank=True), default=list)
  dish_image = models.ImageField(default="", upload_to='dishes')
  cook_time = models.IntegerField(default=0)
  #price = models.IntegerField(default=0)
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)

  def __str__(self):
    return self.title + " (" + str(self.id) + ")"

class Customer(models.Model):
  phone_number = models.CharField(max_length=30, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  favorites = models.ManyToManyField(Dish)

  def __str__(self):
    return "Customer " + self.first_name + " " + self.last_name + " (" + str(self.id) + ")"


class Dish_Review(models.Model):
  dish_rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
  description = models.CharField(max_length=200)
  report_flag = models.BooleanField(default=False)
  customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
  dish = models.ForeignKey(Dish, on_delete=models.CASCADE)

  def __str__(self):
    return self.dish.title + " Review (" + str(self.id) + ")"

class Address(models.Model):
  street_name = models.CharField(max_length=60, default="")
  city = models.CharField(max_length=60, default="")
  state = models.CharField(max_length=20, default="")
  zipcode = models.CharField(max_length=20, default="")
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
