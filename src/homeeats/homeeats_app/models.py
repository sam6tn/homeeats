from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
# from .managers import CustomUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField
import datetime
from django.utils import timezone
import pytz
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
  is_cook = models.BooleanField(default=False)
  is_customer = models.BooleanField(default=False)

'''
Columns in the cook database table. The cook is a type of user, as specified by 
the one-to-one field with the User model
'''
class Cook(models.Model):
  banned = models.BooleanField(default=False)       # False = account has not been banned; True = account has been banned
  approved = models.BooleanField(default=False)     # False = account has not bee approved; True = account has been approved
  online = models.BooleanField(default=False)       # False = cook is not currently accepting orders; True = cook is currently accepting orders
  kitchen_license = models.CharField(max_length=30) # Kitchen license identification code 
  government_id = models.ImageField(default="", upload_to='cook_government_ids') 
  phone_number = models.CharField(max_length=30, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE)  # Each user account can have maximum one relationship with a cook, vice-versa
  delivery_distance_miles = models.IntegerField(default=30)
  delivery_fee = models.DecimalField(default=0, decimal_places=2, max_digits=6)

  def __str__(self):
    return self.user.first_name + " " + self.user.last_name + " (" + str(self.id) + ")"
  

class Cuisine(models.Model):
  name = models.CharField(default="", max_length=30)
  cooks = models.ManyToManyField(Cook, blank=True, related_name="cooks")
  flag = models.ImageField(default="", upload_to='flags')
  def __str__(self):
    return self.name

'''
Columns of the dish database table. Cooks have the ability to generate new dishes in the database table.
'''
class Dish(models.Model):
  # title is the name of the dish
  title = models.CharField(default="", max_length=30) 

  # False = dish is available for order; True = dish is unavailable for order
  cook_disabled = models.BooleanField(default=False)

  # Specifies what kind of food the dish is, e.g. Italian
  cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE)

  description = models.CharField(default="", max_length=200)

  # List of ingredients that compose the dish, stored as an array in the database table
  ingredients = ArrayField(models.CharField(max_length=30, blank=True), default=list)

  dish_image = models.ImageField(default="", upload_to='dishes')

  cook_time = models.IntegerField(default=0)

  price = models.DecimalField(default=0, decimal_places=2, max_digits=6)

  # Specifies the cook that makes the dish
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)

  # Average of all numeric ratings from customers
  rating = models.IntegerField(default=0)

  # False = dish is not vegan; True = dish is vegan
  vegan = models.BooleanField(default=False)
  
  allergies = models.CharField(default="", max_length=200)

  def __str__(self):
    return self.title + " (" + str(self.id) + ")"
  class Meta:
    verbose_name_plural = "Dishes"

'''
Customer model is a type of user account, as specified by the one-to-one field with the user model.
'''
class Customer(models.Model):
  banned = models.BooleanField(default=False) #False = account has not been banned; True = account has been banned
  phone_number = models.CharField(null=False,max_length=10, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE) # Each user account can have maximum one relationship with a customer, vice-versa
  favorites = models.ManyToManyField(Dish, blank=True) #User can have many favorite dish objects
  def __str__(self):
    return self.user.first_name + " " + self.user.last_name + " (" + str(self.id) + ")"

class Dish_Review(models.Model):
  dish_rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
  description = models.CharField(max_length=200)
  report_flag = models.BooleanField(default=False)
  report_reason_choices = [
        ('o', 'Offensive'),
        ('n', 'Not Relevant'),
        ('t', 'Threatening'),
        ('s', 'Spam')
    ]
  report_reason = models.CharField(max_length=1, choices=report_reason_choices, default="")
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
  dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
  date = models.DateTimeField(auto_now_add=True)
  def __str__(self):
    return self.dish.title + " Review (" + str(self.id) + ")"
  class Meta:
    verbose_name = "Dish Review"
    verbose_name_plural = "Dish Reviews"

class Address(models.Model):
  street_name = models.CharField(max_length=60, default="")
  city = models.CharField(max_length=60, default="")
  state = models.CharField(max_length=20, default="")
  zipcode = models.CharField(max_length=20, default="")
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE, blank=True, null=True)
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
  is_cook_address = models.BooleanField(default=False)
  current_customer_address = models.BooleanField(default=False)
  class Meta:
    verbose_name_plural = "Addresses"

class RejectReason(models.Model):
  reason = models.CharField(max_length=60, default="")
  def __str__(self):
    return self.reason

def calculateTime():
  return timezone.localtime(timezone.now()) + datetime.timedelta(minutes=5)

def getOrderDate():
  return timezone.localtime(timezone.now())

class Order(models.Model):
  name = models.CharField(max_length=60, default="") #make it first name <space> last name of customer
  customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)
  item_subtotal = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  homeeats_share = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  cook_share = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  tax = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  tip = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  delivery_fee = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  total = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  special_requests = models.CharField(max_length=120, default="")
  status_choices = [
        ('p', 'Pending'),
        ('c', 'Cooking'),
        ('o', 'Out For Delivery'),
        ('d', 'Delivered'),
        ('r', 'Rejected'),
        ('x', 'Customer Canceled')
    ]
  status = models.CharField(max_length=1, choices=status_choices, default='p')
  date = models.DateTimeField(default=getOrderDate)
  estimated_arrival_time = models.DateTimeField(null=True, blank=True)
  actual_arrival_time = models.DateTimeField(null=True, blank=True)
  pending_deadline = models.DateTimeField(default=calculateTime)
  reject_reason = models.ForeignKey(RejectReason, on_delete=models.CASCADE, null=True, blank=True)
  street_name = models.CharField(max_length=60, default="")
  city = models.CharField(max_length=60, default="")
  state = models.CharField(max_length=20, default="")
  zipcode = models.CharField(max_length=20, default="")
  paid = models.BooleanField(default=False)
  payment_choices = [
        ('a', 'Cash'),
        ('b', 'Card')
    ]
  payment_option = models.CharField(max_length=1, choices=payment_choices, default='a')
  requested_delivery_time = models.DateTimeField(null=True, blank=True)

class Item(models.Model):
  dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
  quantity = models.IntegerField(default=0)
  subtotal = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  order = models.ForeignKey(Order, on_delete=models.CASCADE)
  review = models.OneToOneField(Dish_Review, on_delete=models.CASCADE, null=True, blank=True)

class ShoppingCart(models.Model):
  customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE, null=True, blank=True)
  item_subtotal = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  tax = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  tip = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  total_before_tip = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  total_after_tip = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  empty = models.BooleanField(default=True)
  special_requests = models.CharField(max_length=120, default="")
  paid = models.BooleanField(default=False)
  payment_choices = [
        ('a', 'Cash'),
        ('b', 'Card')
    ]
  payment_option = models.CharField(max_length=1, choices=payment_choices, default='a') 
  requested_delivery_time = models.DateTimeField(null=True, blank=True)

class CartItem(models.Model):
  dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
  quantity = models.IntegerField(default=0)
  subtotal = models.DecimalField(default=0, decimal_places=2, max_digits=6)
  shopping_cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)

class CookChangeRequest(models.Model):
  cook = models.ForeignKey(Cook, on_delete=models.CASCADE)
  kitchen_license = models.CharField(max_length=30)
  phone_number = models.CharField(max_length=30, default="")
  street_name = models.CharField(max_length=60, default="")
  city = models.CharField(max_length=60, default="")
  state = models.CharField(max_length=20, default="")
  zipcode = models.CharField(max_length=20, default="")

class OrderMessage(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  message = models.CharField(max_length=256)
  time = models.DateTimeField(default=getOrderDate)
  order = models.ForeignKey(Order, on_delete=models.CASCADE)