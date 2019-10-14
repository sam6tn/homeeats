from django.contrib import admin
from .models import Cook, Customer, Dish

# Register your models here.

admin.site.register(Cook)
admin.site.register(Customer)
admin.site.register(Dish)