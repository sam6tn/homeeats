from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from .managers import CustomUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField
import datetime
from django.utils import timezone
import pytz

class User(AbstractUser):
  is_cook = models.BooleanField(default=False)
  is_customer = models.BooleanField(default=False)

'''
Columns in the cook database table
'''
class Cook(models.Model):
  banned = models.BooleanField(default=False)
  approved = models.BooleanField(default=False)
  online = models.BooleanField(default=False)
  kitchen_license = models.CharField(max_length=30)
  government_id = models.ImageField(default="", upload_to='cook_government_ids')
  phone_number = models.CharField(max_length=30, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  def __str__(self):
    return self.user.first_name + " " + self.user.last_name + " (" + str(self.id) + ")"
  delivery_distance_miles = models.IntegerField(default=30)
  delivery_fee = models.DecimalField(default=0, decimal_places=2, max_digits=6)

class Cuisine(models.Model):
  name = models.CharField(default="", max_length=30)
  cooks = models.ManyToManyField(Cook, blank=True, related_name="cooks")
  flag = models.ImageField(default="", upload_to='flags')
  def __str__(self):
    return self.name + " cuisine (" + str(self.id) + ")"

class Dish(models.Model):
  title = models.CharField(default="", max_length=30)
  cook_disabled = models.BooleanField(default=False)
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

  def __str__(self):
    return self.title + " (" + str(self.id) + ")"
  class Meta:
    verbose_name_plural = "Dishes"

class Customer(models.Model):
  banned = models.BooleanField(default=False)
  phone_number = models.CharField(max_length=30, default="")
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  favorites = models.ManyToManyField(Dish, blank=True)
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

# class Message(models.Model):
#      sender = models.ForeignKey(User, related_name="sender")
#      reciever = # almost same as above field, just change the related-name
#      msg_content = # text field 
#      created_at = # time field

# def deserialize_user(user):
#     """Deserialize user instance to JSON."""
#     return {
#         'id': user.id, 'username': user.username, 'email': user.email,
#         'first_name': user.first_name, 'last_name': user.last_name
#     }


# class TrackableDateModel(models.Model):
#     """Abstract model to Track the creation/updated date for a model."""

#     create_date = models.DateTimeField(auto_now_add=True)
#     update_date = models.DateTimeField(auto_now=True)

#     class Meta:
#         abstract = True


# def _generate_unique_uri():
#     """Generates a unique uri for the chat session."""
#     return str(uuid4()).replace('-', '')[:15]


# class ChatSession(TrackableDateModel):
#     """ A Chat Session. The uri's are generated by taking the first 15 characters from a UUID """

#     owner = models.ForeignKey(User, on_delete=models.PROTECT)
#     uri = models.URLField(default=_generate_unique_uri)


# class ChatSessionMessage(TrackableDateModel):
#     """Store messages for a session."""

#     user = models.ForeignKey(User, on_delete=models.PROTECT)
#     chat_session = models.ForeignKey(
#         ChatSession, related_name='messages', on_delete=models.PROTECT
#     )
#     message = models.TextField(max_length=2000)

#     def to_json(self):
#         """deserialize message to JSON."""
#         return {'user': deserialize_user(self.user), 'message': self.message}


# class ChatSessionMember(TrackableDateModel):
#     """Store all users in a chat session."""

#     chat_session = models.ForeignKey(
#         ChatSession, related_name='members', on_delete=models.PROTECT
#     )
#     user = models.ForeignKey(User, on_delete=models.PROTECT)