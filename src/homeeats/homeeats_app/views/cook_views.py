from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .. import models
from ..models import User
from .. import forms
from ..models import Cook, Cuisine, Dish, Order, Customer, Item
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.forms import model_to_dict
from django.contrib.auth.decorators import login_required
from ..decorators import cook_required
from django.contrib import messages

#cook home page after login
@login_required
@cook_required
def manage(request): 
  cuisines = get_cuisines_by_cook(request)
  cook = model_to_dict(get_object_or_404(Cook, user_id=request.user.id))
  context = {  #pass in context
    'cuisines': cuisines,
    'cook': cook
  }
  return render(request, 'cook_templates/cook_manage.html', context)

@login_required
@cook_required
def home(request):
  orders = get_orders_by_cook(request)
  cook = model_to_dict(get_object_or_404(Cook, user_id=request.user.id))
  context = {
    'orders': orders,
    'cook': cook
  }
  return render(request, 'cook_templates/cook_home.html', context)

@login_required
@cook_required
def single_order_view(request, order_id):
  items = get_items_by_order(order_id)
  cook = model_to_dict(get_object_or_404(Cook, user_id=request.user.id))
  context = {
    'order_id': order_id,
    'items': items,
    'cook': cook
  }
  return render(request, 'cook_templates/single_order_view.html', context)

@login_required
@cook_required
def create_dish(request):
  cook = get_object_or_404(Cook, user_id=request.user.id)
  if request.method == 'POST':
      form = forms.DishCreateForm(request.POST, request.FILES)
      if form.is_valid():
        data = form.cleaned_data
        dish = Dish.objects.create(
          title=data['title'], 
          cuisine=data['cuisine'], 
          description=data['description'],
          dish_image=data['dish_image'],
          ingredients=data['ingredients'],  
          price=data['price'], 
          cook_time=data['cook_time'],
          vegan=data['vegan'],
          allergies=data['allergies'],
          cook=cook
          )
        dish.save()
        objs = Cuisine.objects.filter(cooks__in=[cook])
        if(data['cuisine'] not in objs): #add cook to cuisine if doesn't already exist
          data['cuisine'].cooks.add(cook)
        return HttpResponseRedirect(reverse('cook_manage'))
      else:
        return render(request, 'cook_templates/create_dish.html', {'form': form, 'cook': model_to_dict(cook)})
  else:
    form = forms.DishCreateForm()
    return render(request, 'cook_templates/create_dish.html', {'form':form, 'cook': model_to_dict(cook)})

@login_required
@cook_required
def delete_dish(request, dish_id):
  dish = Dish.objects.get(id=dish_id)
  cuisine = Cuisine.objects.get(id=dish.cuisine_id)
  cook = Cook.objects.get(user_id=request.user.id)
  if (dish.cook == cook): #only allow a cook to delete his/her own dish
    dish.delete()
    objs = Dish.objects.filter(cook=cook, cuisine=cuisine)
    if not objs: #check if they are deleting the only dish left in the cuisine
      cuisine.cooks.remove(cook) #if so, remove them from the cuisine
      return HttpResponseRedirect(reverse('cook_manage')) #cuisine doesn't exist so redirect to cook/manage
    return HttpResponseRedirect(reverse('cook_cuisine_dishes', args=[cuisine.id])) #redirect to cuisine because it exists
  return HttpResponseRedirect(reverse('cook_manage'))

def get_items_by_order(order_id):
  objs = Item.objects.filter(order=order_id)
  items = []
  for obj in objs:
    dish = Dish.objects.get(id=obj.dish_id)
    converted_dish = model_to_dict(dish)
    converted = model_to_dict(obj)
    converted['dish'] = converted_dish
    items.append(converted)
  return items

def get_orders_by_cook(request):
  cook = get_object_or_404(Cook, user_id=request.user.id)
  objs = Order.objects.filter(cook=cook)
  orders = []
  for obj in objs:
    orders.append(model_to_dict(obj))
  return orders

def get_cuisines_by_cook(request):
  cook = get_object_or_404(Cook, user_id=request.user.id)
  objs = Cuisine.objects.filter(cooks__in=[cook])
  cuisines = []
  for obj in objs:
    cuisines.append(model_to_dict(obj))
  return cuisines

@login_required
@cook_required
def cook_cuisine_dishes(request, cuisine_id):
  cook = get_object_or_404(Cook, user_id=request.user.id)
  cuisine = get_object_or_404(Cuisine, id=cuisine_id)
  objs = Dish.objects.filter(cook=cook, cuisine=cuisine)
  dishes = []
  for obj in objs:
    dishes.append(model_to_dict(obj))
  context = {  #pass in context
    'cook': model_to_dict(cook),
    'dishes': dishes,
    'cuisine': cuisine.name
  }
  return render(request, 'cook_templates/cook_cuisine_dishes.html', context)

#set online/offline for cook
@login_required
@cook_required
def available(request):
  cook = get_object_or_404(Cook, user_id=request.user.id)
  if cook.online == True:
    orders = Order.objects.filter(cook=cook)
    for order in orders:
      if order.status == 'p' or order.status == 'o' or order.status == 'c':
        messages.add_message(request, messages.ERROR, 'cook_online_cant_go_offline')
        return HttpResponseRedirect(reverse('cook_home')) 
    cook.online = False
    cook.save()
  else:
    cook.online = True
    cook.save()

  return HttpResponseRedirect(reverse('cook_home'))  

@login_required
@cook_required
def accept_order(request, order_id):
  change_order_status('p', 'c', request, order_id)
  return HttpResponseRedirect(reverse('cook_home'))

@login_required
@cook_required
def reject_order(request, order_id):
  change_order_status('p', 'r', request, order_id)
  return HttpResponseRedirect(reverse('cook_home'))

@login_required
@cook_required
def cooking_to_delivery(request, order_id):
  change_order_status('c', 'o', request, order_id)
  return HttpResponseRedirect(reverse('cook_home'))

@login_required
@cook_required
def completed_delivery(request, order_id):
  change_order_status('o', 'd', request, order_id)
  return HttpResponseRedirect(reverse('cook_home'))

#helper method to change a status from previous to new
def change_order_status(previous, new, request, order_id):
  cook = get_object_or_404(Cook, user_id=request.user.id)
  order = get_object_or_404(Order, id=order_id)
  if order.cook == cook and order.status == previous: #make sure this order belongs to this cook
    order.status = new
    order.save()





