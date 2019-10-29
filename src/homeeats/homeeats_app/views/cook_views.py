from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from .. import forms
from ..models import Cook, Cuisine, Dish, Order, Customer, Item
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.forms import model_to_dict
from django.contrib.auth.decorators import login_required

#cook home page after login
@login_required
def manage(request): 
  cuisines = get_cuisines_by_cook(request)
  context = {  #pass in context
    'cuisines': cuisines
  }
  return render(request, 'cook_templates/cook_manage.html', context)

@login_required
def home(request):
  orders = get_orders_by_cook(request)
  context = {
    'orders': orders
  }
  return render(request, 'cook_templates/cook_home.html', context)

@login_required
def single_order_view(request, order_id):
  items = get_items_by_order(order_id)
  context = {
    'order_id': order_id,
    'items': items
  }
  return render(request, 'cook_templates/single_order_view.html', context)

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

def cook_cuisine_dishes(request, cuisine_id):
  cook = get_object_or_404(Cook, user_id=request.user.id)
  cuisine = get_object_or_404(Cuisine, id=cuisine_id)
  objs = Dish.objects.filter(cook=cook, cuisine=cuisine)
  dishes = []
  for obj in objs:
    dishes.append(model_to_dict(obj))
  context = {  #pass in context
    'dishes': dishes,
    'cuisine': cuisine.name
  }
  return render(request, 'cook_templates/cook_cuisine_dishes.html', context)


