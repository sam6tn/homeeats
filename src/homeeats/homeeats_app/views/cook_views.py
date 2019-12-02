from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .. import models
from ..models import User
from .. import forms
from ..models import Cook, Cuisine, Dish, Order, Customer, Item, Dish_Review, Address
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.forms import model_to_dict
from django.contrib.auth.decorators import login_required
from ..decorators import cook_required
from django.contrib import messages
import datetime

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
  pending_orders = []
  in_progress_orders = []
  deadline = datetime.datetime.now()
  for order in orders:
    if order['status'] == 'p':
      print(order)
      pending_orders.append(order)
      deadline = order['pending_deadline']
    elif order['status'] == 'o' or order['status'] == 'c':
      in_progress_orders.append(order)

  #test timer crap
  # deadline = datetime.datetime.now() + datetime.timedelta(minutes=5)

  context = {
    'pending_orders': pending_orders,
    'in_progress_orders': in_progress_orders,
    'cook': cook,
    'deadline': deadline
  }
  return render(request, 'cook_templates/cook_home.html', context)

@login_required
@cook_required
def single_order_view(request, order_id):
  items = get_items_by_order(order_id)
  cook = model_to_dict(get_object_or_404(Cook, user_id=request.user.id))
  order = Order.objects.get(id=order_id)
  customer = Customer.objects.get(id=order.customer_id)
  user = customer.user
  address = Address.objects.get(customer=customer)
  context = {
    'user': user,
    'customer': customer,
    'address': address,
    'order': order,
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

@login_required
@cook_required
def reviews_for_dish(request, dish_id):
  dish = get_object_or_404(Dish, id=dish_id)
  objs = Dish_Review.objects.filter(dish=dish, report_flag=False).order_by('-date')
  reviews = []
  for obj in objs:
    rev = model_to_dict(obj)
    rev['date'] = obj.date.strftime("%m/%d/%y")
    reviews.append(rev)
  for review in reviews:
    customer = Customer.objects.get(id=review['customer'])
    user = User.objects.get(id=customer.user_id)
    review['user'] = model_to_dict(user)
  context = {
    'dish': model_to_dict(dish),
    'reviews': reviews
  }
  return render(request, 'cook_templates/cook_dish_reviews.html', context)

@login_required
@cook_required
def report_dish_review(request, dish_review_id, reason):
  dish_review = Dish_Review.objects.get(id=dish_review_id)
  dish_review.report_flag=True
  dish_review.report_reason=reason
  dish_review.save()
  messages.add_message(request, messages.ERROR, 'Dish review has been flagged to be further evaluated')
  return HttpResponseRedirect(reverse('reviews_for_dish', args=[dish_review.dish_id]))

@login_required
@cook_required
def cook_disable_dish(request, dish_id):
  dish = Dish.objects.get(id=dish_id)
  cook = Cook.objects.get(user_id=request.user.id)
  if dish.cook == cook:
    dish.cook_disabled = True
    dish.save()
  return HttpResponseRedirect(reverse('cook_cuisine_dishes', args=[dish.cuisine_id]))

@login_required
@cook_required
def cook_enable_dish(request, dish_id):
  dish = Dish.objects.get(id=dish_id)
  cook = Cook.objects.get(user_id=request.user.id)
  if dish.cook == cook:
    dish.cook_disabled = False
    dish.save()
  return HttpResponseRedirect(reverse('cook_cuisine_dishes', args=[dish.cuisine_id]))

@login_required
@cook_required
def cook_edit_dish(request, dish_id):
  dish = Dish.objects.get(id=dish_id)
  cook = Cook.objects.get(user_id=request.user.id)
  if dish.cook != cook:
    return HttpResponseRedirect(reverse('cook_manage'))
  if request.method == 'POST':
    form = forms.DishEditForm(request.POST, request.FILES, instance=dish)
    if form.is_valid():
      dish = form.save(commit=False)
      dish.cook = cook
      dish.save()
      return HttpResponseRedirect(reverse('cook_cuisine_dishes', args=[dish.cuisine_id]))
  else:
    form = forms.DishEditForm(instance=dish)
  return render(request, 'cook_templates/cook_edit_dish.html', {'form': form, 'cuisine_id': dish.cuisine_id})

@login_required
@cook_required
def myaccount(request):
  if request.method == 'POST':
    first_name = request.GET.get('first_name')
    last_name = request.GET.get('last_name')
    username = request.GET.get('username')
    print('first_name: ' , first_name)
    #return HttpResponseRedirect(reverse('customer_edit_profile'))
  return render(request, 'cook_templates/cook_profile.html')

def order_history(request):
  cook = Cook.objects.get(user_id=request.user.id)
  objs = Order.objects.filter(cook=cook, status='r').order_by('-date')
  objs2 = Order.objects.filter(cook=cook, status='d').order_by('-date')
  rejected_orders = []
  completed_orders = []
  for obj in objs:
    ord = model_to_dict(obj)
    ord['date'] = obj.date.strftime("%m/%d/%y")
    rejected_orders.append(ord)
  for obj in objs2:
    ord = model_to_dict(obj)
    ord['date'] = obj.date.strftime("%m/%d/%y")
    completed_orders.append(ord)
  context = {
    'rejected_orders': rejected_orders,
    'completed_orders': completed_orders
  }

  return render(request, 'cook_templates/order_history.html', context)
  
