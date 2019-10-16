from django.contrib import admin
from .models import Cook, Customer, Dish, Dish_Review

# Register your models here.

admin.site.register(Cook)
admin.site.register(Customer)
admin.site.register(Dish)
admin.site.register(Dish_Review)
