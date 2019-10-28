from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Cook, Customer, Dish, Dish_Review, Cuisine

admin.site.site_header = "HomeEats Admin Page"

#Customizing the display and possible filters when looking through each of these models from the admin page
class DishAdmin(admin.ModelAdmin):
	list_display = ('title', 'cuisine', 'cook')
	list_filter = ('cuisine',)

class CookAdmin(admin.ModelAdmin):
	list_display = ('user', 'approved', 'kitchen_license')

class CustomerAdmin(admin.ModelAdmin):
	list_display = ('user', 'phone_number')


# Register your models here.
admin.site.unregister(Group)
admin.site.register(Cook, CookAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Dish_Review)
#admin.site.register(Cuisine)
