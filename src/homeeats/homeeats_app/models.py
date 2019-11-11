from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from .managers import CustomUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField

class User(AbstractUser):
  is_cook = models.BooleanField(default=False)
  is_customer = models.BooleanField(default=False)

'''
Columns in the cook database table
'''
class Cook(models.Model):
  approved = models.BooleanField(default=False)
  online = models.BooleanField(default=False)
  kitchen_license = models.CharField(max_length=30)
  phone_number = models.CharField(max_length=30, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  def __str__(self):
    return "Cook " + self.user.first_name + " " + self.user.last_name + " (" + str(self.id) + ")"
  delivery_distance_miles = models.IntegerField(default=30)

class Cuisine(models.Model):
  name = models.CharField(default="", max_length=30)
  cooks = models.ManyToManyField(Cook, blank=True, related_name="cooks")
  def __str__(self):
    return self.name + " cuisine (" + str(self.id) + ")"

class Dish(models.Model):
  title = models.CharField(default="", max_length=30)
  cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE)
  description = models.CharField(default="", max_length=200)
  ingredients = ArrayField(models.CharField(max_length=30, blank=True), default=list)
  dish_image = models.ImageField(default="", upload_to='dishes')
  cook_time = models.IntegerField(default=0)
  price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)
  rating = models.IntegerField(default=0)
  vegan = models.BooleanField(default=False)
  allergies = models.CharField(default="", max_length=200)
  # total_rating = models.IntegerField(default=0)
  # num_ratings = models.IntegerField(default=0)

  def __str__(self):
    return self.title + " (" + str(self.id) + ")"
  class Meta:
    verbose_name_plural = "Dishes"

class Customer(models.Model):
  phone_number = models.CharField(max_length=30, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  favorites = models.ManyToManyField(Dish, blank=True)
  def __str__(self):
    return "Customer " + self.user.first_name + " " + self.user.last_name + " (" + str(self.id) + ")"

class Dish_Review(models.Model):
  dish_rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
  description = models.CharField(max_length=200)
  report_flag = models.BooleanField(default=False)
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
  dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
  def __str__(self):
    return self.dish.title + " Review (" + str(self.id) + ")"
  class Meta:
    verbose_name = "Dish Review"
    verbose_name_plural = "Dish Reviews"
  date = models.DateTimeField(auto_now_add=True)

class Address(models.Model):
  street_name = models.CharField(max_length=60, default="")
  city = models.CharField(max_length=60, default="")
  state = models.CharField(max_length=20, default="")
  zipcode = models.CharField(max_length=20, default="")
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE, blank=True, null=True)
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
  is_cook_address = models.BooleanField(default=False)

class Order(models.Model):
  name = models.CharField(max_length=60, default="") #make it first name <space> last name of customer
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)
  total = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  special_requests = models.CharField(max_length=120, default="")
  status_choices = [
        ('p', 'Pending'),
        ('c', 'Cooking'),
        ('o', 'Out For Delivery'),
        ('d', 'Delivered'),
        ('r', 'Rejected')
    ]
  status = models.CharField(max_length=1, choices=status_choices, default='p')
  date = models.DateTimeField(auto_now_add=True)

class Item(models.Model):
  dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
  quantity = models.IntegerField(default=0)
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  