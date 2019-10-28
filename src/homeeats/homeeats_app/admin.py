from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Cook, Customer, Dish, Dish_Review, Cuisine

admin.site.site_header = "HomeEats Admin Page"
# Register your models here.
admin.site.unregister(Group)
admin.site.register(Cook)
admin.site.register(Customer)
admin.site.register(Dish)
admin.site.register(Dish_Review)
admin.site.register(Cuisine)
