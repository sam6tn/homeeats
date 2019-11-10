from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Cook, Customer, Dish, Dish_Review, Cuisine, Order, Item, Address
from django.dispatch import receiver
from django.db.models.signals import pre_delete

admin.site.site_header = "HomeEats Admin Page"

#Customizing the display and possible filters when looking through each of these models from the admin page
class DishAdmin(admin.ModelAdmin):
	list_display = ('title', 'cuisine', 'cook')
	list_filter = ('cuisine',)

class CookAdmin(admin.ModelAdmin):
	list_display = ('user', 'approved', 'kitchen_license')

class CustomerAdmin(admin.ModelAdmin):
	list_display = ('user', 'phone_number')

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

# Register your models here.
admin.site.unregister(Group)
admin.site.register(Cook, CookAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Dish_Review)
admin.site.register(Cuisine)
admin.site.register(Order)
admin.site.register(Item)
admin.site.register(Address)
