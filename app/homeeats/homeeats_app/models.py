from django.db import models
#from django.contrib.postgres.fields import ArrayField

class Address(models.Model):
  street_address = models.CharField(max_length=60) 

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
#  cuisines = ArrayField(
#            models.CharField(max_length=10, blank=True),
#            null=True
#          )

