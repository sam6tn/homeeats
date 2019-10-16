from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

#class CustomUser(AbstractUser):
#  username = None
#  email = models.EmailField(_('email_address'), unique=True)
#
#  USERNAME_FIELD = 'email'
#  REQUIRED_FIELDS = []
#  objects = CustomUserManager()
#
#  def __str__(self):
#    return self.email

class Cook(models.Model):
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30, null = True)
  approved = models.BooleanField(default=False)
  kitchen_license = models.CharField(max_length=30)
  phone_number = models.CharField(max_length=30, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  email = models.EmailField(blank=False,unique=True,null=False,default="")
  password = models.CharField(max_length=30,null=False,blank=False,default="")

class Dish(models.Model):
  title = models.CharField(max_length=30)

class Customer(models.Model):
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)
  phone_number = models.CharField(max_length=30, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  email = models.EmailField(blank=False,unique=True,null=False,default="")
  password = models.CharField(max_length=30,null=False,blank=False,default="")
  favorites = models.ManyToManyField(Dish)

  def __str__(self):
    return self.last_name + ", " + self.first_name

class Dish_Review(models.Model):
  dish_rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
  description = models.CharField(max_length=200)
  report_flag = models.BooleanField(default=False)
  customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
  dish = models.ForeignKey(Dish, on_delete=models.CASCADE)

class Address(models.Model):
  street_name = models.CharField(max_length=60, default="")
  city = models.CharField(max_length=60, default="")
  state = models.CharField(max_length=20, default="")
  zipcode = models.CharField(max_length=20, default="")
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
