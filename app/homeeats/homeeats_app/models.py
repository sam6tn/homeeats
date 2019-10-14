from django.db import models
from django.contrib.postgres.fields import ArrayField

class Address(models.Model):
  street_address = models.CharField(max_length=60) 

# Adding customer class model with basic information
class Customer(models.Model):
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)
  email = models.CharField(max_length=30)
  password = models.CharField(max_length=30)

#Adding Dish model with basic attributes
class Dish(models.Model):
  title = models.CharField(max_length= 90)
  cuisine = models.CharField(max_length = 60)
  description = models.CharField(max_length = 90)
class Admin(models.Model):
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)
  admin_id = models.CharField(max_length=15)


class Cook(models.Model):
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)
  email = models.CharField(max_length=30)
  password = models.CharField(max_length=30)
  address = models.OneToOneField(
    Address,
    on_delete=models.CASCADE,
    primary_key=True,
  )
  approved = models.BooleanField(default=False)
  kitchen_license = models.CharField(max_length=30)
  cuisines = ArrayField(
            models.CharField(max_length=10, blank=True),
          )

