from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Cook, Customer, Dish, Dish_Review, Cuisine, Order, Item, Address, User
from django.dispatch import receiver
from django.db.models.signals import pre_delete

#Changing the site titles of the admin log in page and landing page 
admin.site.site_header = "HomeEats Admin Page"
admin.site.index_title = "HomeEats Administration"

#Customizing the display and possible filters when looking through each of these models from the admin page
#Search_fields will query the set and filter search the result test
#list_display organizes columns of the tables that the admin sees for each model
#list_filter is a box on the right of the page with preset filters for the data entries

#Update dish rating upon review deletion
@receiver(pre_delete, sender=Dish_Review)
def _Dish_Review_delete(sender, instance, **kwargs):
	print("Deleting dish review")
	dish = instance.dish
	dish_reviews = Dish_Review.objects.filter(dish=dish).exclude(id=instance.id)
	total_rating = 0
	if len(dish_reviews)==0:
		new_rating = 0
	else:
		for review in dish_reviews:
			total_rating += review.dish_rating
			new_rating = int(round(total_rating/len(dish_reviews)))
	dish.rating = new_rating
	print(dish.rating)
	dish.save()

#Customizing the Dish Page
class DishAdmin(admin.ModelAdmin):
	#search_fields = ['title', 'cuisine', 'cook', 'price']	
	list_display = ('title', 'cuisine', 'cook', 'cook_time', 'price')	
	list_filter = ('cuisine', 'cook_time', 'price',)

#Customizing the Cook Page
class CookAdmin(admin.ModelAdmin):
	list_display = ('user', 'approved', 'kitchen_license')

#Customizing the Customer Page
class CustomerAdmin(admin.ModelAdmin):
	#search_fields = ['phone_number']
	list_display = ('user', 'phone_number')

#Customizing the Order Page
class OrderAdmin(admin.ModelAdmin):
	#search_fields = ['name']
	list_display = ('name', 'status', 'cook', 'customer', 'total')
	list_filter = ('status',)

#Customizing the Item Page
class ItemAdmin(admin.ModelAdmin):
	#search_fields = ['dish', 'quantity', 'order']
	list_display = ('dish', 'quantity', 'order')
	list_filter = ('dish',)
#Customizing the Address Page
class AddressAdmin(admin.ModelAdmin):
	#search_fields = ['cook', 'customer', 'zipcode']
	list_display = ('cook', 'customer', 'city', 'state', 'zipcode')
	list_filter = ('state',)

#Customizing the Dish Reviw Page
class DishReviewAdmin(admin.ModelAdmin):
	#search_fields = ['dish']
	list_display = ('dish_rating', 'report_flag', 'customer', 'dish')
	list_filter = ('dish_rating',)

# Register all the models here.
# Unregistered the Group model (default)
admin.site.unregister(Group)
admin.site.register(Cook, CookAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Dish_Review, DishReviewAdmin)
admin.site.register(Cuisine)
admin.site.register(Order, OrderAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(User)