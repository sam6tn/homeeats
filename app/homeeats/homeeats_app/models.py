from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator

class Cook(models.Model):
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)
  email = models.CharField(max_length=30)
  password = models.CharField(max_length=30)
  approved = models.BooleanField(default=False)
  kitchen_license = models.CharField(max_length=30)
#  cuisines = ArrayField(
#            models.CharField(max_length=10, blank=True),
#            null=True
#          )

class Customer(models.Model):
  first_name = models.CharField(max_length=30)

class Dish(models.Model):
  title = models.CharField(max_length=30)

class Dish_Review(models.Model):
  dish_rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
  description = models.CharField(max_length=200)
  report_flag = models.BooleanField(default=False)
  customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
  dish = models.ForeignKey(Dish, on_delete=models.CASCADE)

class Address(models.Model):
  street_address = models.CharField(max_length=60) 
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE)