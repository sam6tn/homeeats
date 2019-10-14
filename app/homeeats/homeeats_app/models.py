from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator

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
  cuisines = ArrayField(
            models.CharField(max_length=10, blank=True),
          )


class Customer(models.Model):
  first_name = models.CharField(max_length=30)
  last_name = models.CharField(max_length=30)
  email = models.EmailField()
  password = models.CharField(max_length=30)
  addresses = models.ManyToManyField(
    Address,
    on_delete=models.CASCADE,
    primary_key=True,
  )
  favorites = models.ManyToManyField(
    Dish,
    on_delete=models.CASCADE,
    primary_key=True,
  )
  reviews = models.ManyToManyField(
    Dish_Review,
    on_delete=models.CASCADE,
    primary_key=True,
  )
  user = models.OneToOneField(User,
  on_delete=models.CASCADE,blank=True, null=True)

  def __str__(self):
    return self.last_name + ", " + self.first_name

  @receiver(post_save, sender=User)
  def create_user_profile(sender, instance, created, **kwargs):
    if created:
      Profile.objects.create(user=instance)
  
class Dish(models.Model):
  title = models.CharField(max_length=30)

class Dish_Review(models.Model):
  dish_rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
  description = models.CharField(max_length=200)
  report_flag = models.BooleanField(default=False)
  customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
  dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
