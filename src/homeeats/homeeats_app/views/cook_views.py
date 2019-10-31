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

#cook home page after login
@login_required
@cook_required
def manage(request): 
  cuisines = get_cuisines_by_cook(request)
  context = {  #pass in context
    'cuisines': cuisines
  }
  return render(request, 'cook_templates/cook_manage.html', context)

@login_required
@cook_required
def home(request):
  orders = get_orders_by_cook(request)
  context = {
    'orders': orders
  }
  return render(request, 'cook_templates/cook_home.html', context)

@login_required
@cook_required
def single_order_view(request, order_id):
  items = get_items_by_order(order_id)
  context = {
    'order_id': order_id,
    'items': items
  }
  return render(request, 'cook_templates/single_order_view.html', context)

@login_required
@cook_required
def create_dish(request):
  cook = get_object_or_404(Cook, user_id=request.user.id)
  if request.method == 'POST':
      form = forms.DishCreateForm(request.POST)
      if form.is_valid():
        data = form.cleaned_data
        dish = Dish.objects.create(
          title=data['title'], 
          cuisine=data['cuisine'], 
          description=data['description'], 
          ingredients=data['ingredients'],  
          price=data['price'], 
          cook_time=data['cook_time'],
          cook=cook
          )
        dish.save()
        objs = Cuisine.objects.filter(cooks__in=[cook])
        if(data['cuisine'] not in objs): #add cook to cuisine if doesn't already exist
          data['cuisine'].cooks.add(cook)
        return HttpResponseRedirect(reverse('cook_manage'))
      else:
        return render(request, 'cook_templates/create_dish.html', {'form': form})
  else:
    form = forms.DishCreateForm()
    return render(request, 'cook_templates/create_dish.html', {'form':form})

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
    'dishes': dishes,
    'cuisine': cuisine.name
  }
  return render(request, 'cook_templates/cook_cuisine_dishes.html', context)


