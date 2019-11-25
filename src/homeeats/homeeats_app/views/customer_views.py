from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.template import loader
from ..forms import CustomerCreateForm, DishReviewForm, UserEditForm, AddressEditForm, PhoneEditForm
from .. import forms
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from ..models import Dish, Customer, Dish_Review, Cook, Address, ShoppingCart, CartItem, Order, Item
from .. import models
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from ..decorators import customer_required
from django.forms import model_to_dict
from django.views.generic import UpdateView
from django.urls import reverse_lazy
import urllib.request
import urllib.parse
import json
import ssl
from django.http import Http404

@login_required
@customer_required
def dish(request, dish_id):
    dish = Dish.objects.get(id=dish_id) #get Dish object from dish_id
    customer = Customer.objects.get(user_id=request.user.id)
    if(dish.cook_disabled or dish.cook.online == False or (not customer.shoppingcart.empty and customer.shoppingcart.cook != dish.cook)):
      raise Http404()
    reviews = dish.dish_review_set.filter(report_flag=False) #get all reviews for that Dish
    form = DishReviewForm()
    return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews':reviews, 'form':form})

# @login_required
# @customer_required
# def checkout(request):
#   return render(request, 'customer_templates/checkout.html')

@login_required
@customer_required
def home(request):
    customer = Customer.objects.get(user_id=request.user.id)
    if request.method == 'POST':
      form = forms.DishSearchForm(request.POST)
      if form.is_valid():
        dishes = find_nearby_dishes(request)
        data = form.cleaned_data
        search = data['search']
        sort = data['sort']
        cuisine = data['cuisine']
        if search=="" and sort=="" and cuisine=="":
          search = request.POST["search"]

        dishes = dishes.filter(title__icontains=search)
        dishes = dishes.filter(cook_disabled = False)

        if (not customer.shoppingcart.empty):
          dishes = dishes.filter(cook=customer.shoppingcart.cook)

        if (cuisine != 'none' and cuisine !=''):
          dishes = dishes.filter(cuisine=cuisine)

        if (sort == 'rating'):
          dishes = dishes.order_by('-rating')
        elif (sort == 'price'):
          dishes = dishes.order_by('price')
        elif (sort == 'reverse_price'):
          dishes = dishes.order_by('-price')

        return render(request, 'customer_templates/customer_home.html', {'dishes':dishes, 'form': form, 'customer':customer})
      else:
        dishes = find_nearby_dishes(request)
        return render(request, 'customer_templates/customer_home.html', {'dishes': dishes, 'form': form, 'customer':customer})

    else:
      form = forms.DishSearchForm()
      dishes = find_nearby_dishes(request)
      dishes = dishes.filter(cook_disabled = False)
      dishes = dishes.filter(cook__online = True)
      if (not customer.shoppingcart.empty):
        dishes = dishes.filter(cook=customer.shoppingcart.cook)
      dishes=dishes.order_by('-rating')
      
      return render(request, 'customer_templates/customer_home.html', {'dishes': dishes, 'form':form, 'customer':customer})

@login_required
@customer_required
def addtocart(request):
  dish = Dish.objects.get(id=request.POST["dish_id"])
  return_quantity = -1
  if request.method == "POST":
    if(dish.cook_disabled or dish.cook.online == False):
      raise Http404()
    customer = Customer.objects.get(user_id=request.user.id)
    shopping_cart = customer.shoppingcart
    shopping_cart.total += dish.price
    existing_already = False
    for existing_item in shopping_cart.cartitem_set.all(): 
      if (existing_item.dish == dish): #dish already in cart so add to existing cart item
        existing_item.quantity += 1
        existing_item.subtotal += dish.price
        existing_item.save()
        existing_already = True
        return_quantity = existing_item.quantity
        break
    if (existing_already == False): #dish not yet in cart so create new cart item
      cart_item = CartItem.objects.create(
        dish=dish,
        quantity=1,
        subtotal=dish.price,
        shopping_cart=shopping_cart
      )
      return_quantity = 1
      cart_item.save()
      shopping_cart.cook = dish.cook
    shopping_cart.empty = False
    shopping_cart.save()
  data = {
    'quantity': return_quantity,
    'dish_id': request.POST["dish_id"]
  }
  return JsonResponse(data)


@login_required
@customer_required
def toggle_favorite(request):
  if request.method == "POST":
    dish = Dish.objects.get(id=request.POST["dish_id"])
    customer = Customer.objects.get(user_id=request.user.id)
    if dish in customer.favorites.all():
      customer.favorites.remove(dish)
      customer.save()
      data = {
        'status':dish.title + ' favorite removed'
      }
    else:
      customer.favorites.add(dish)
      customer.save()
      data = {
        'status':dish.title + ' favorite added'
      }
  
  return JsonResponse(data)


@login_required
@customer_required
def cart(request):
  customer = Customer.objects.get(user_id=request.user.id)
  cart = customer.shoppingcart
  return render(request, 'customer_templates/cart.html', {'cart':cart})

@login_required
@customer_required
def payment(request):
  customer = Customer.objects.get(user_id=request.user.id)
  cart = customer.shoppingcart
  return render(request, 'customer_templates/payment.html', {'cart':cart})

@login_required
@customer_required
def removeItem(request):
  item = CartItem.objects.get(id=request.POST["item_id"])
  customer = Customer.objects.get(user_id=request.user.id)
  cart = customer.shoppingcart
  cart.total = cart.total - item.subtotal
  if cart.total == 0:
    cart.cook_id = None
    cart.empty = True
  item.delete()
  cart.save()
  return HttpResponse(202, 'ok')

@login_required
@customer_required
def orders(request):
  customer = Customer.objects.get(user_id=request.user.id)
  orders = customer.order_set.all()
  current_orders = customer.order_set.filter(Q(status='p') | Q(status='c') | Q(status='o'))
  past_orders = customer.order_set.filter(Q(status='d') | Q(status='r'))
  return render(request, 'customer_templates/orders.html', {'current_orders':current_orders,'past_orders':past_orders})

@login_required
@customer_required
def order(request, order_id):
  order = Order.objects.get(id=order_id)
  if request.method == "POST":
    form = DishReviewForm(request.POST)
    if form.is_valid():
      data = form.cleaned_data
      dish_id = request.POST["dish_id"]
      dish = Dish.objects.get(id=dish_id)
      item = order.item_set.get(dish=dish)
      rating_name = "rating"+dish_id
      #rating = data["dish_rating"]
      rating = request.POST[rating_name]
      text = data["description"]
      report = False
      customer = Customer.objects.get(user_id=request.user.id)
      
      #save the new review
      dr = Dish_Review(dish_rating=rating,description=text,report_flag=report,customer=customer,dish=dish)
      dr.save()

      #add review to item
      item.review = dr
      item.save()

      #calculate new dish rating
      all_dish_reviews = Dish_Review.objects.filter(dish=dish)
      total_rating = 0
      for review in all_dish_reviews:
        total_rating += review.dish_rating
      new_rating = int(round(total_rating/len(all_dish_reviews)))
      dish.rating = new_rating
      dish.save()

    return HttpResponseRedirect(reverse('order', kwargs={'order_id':order_id}))
  else:
    form = DishReviewForm()
    reviewed_items = order.item_set.filter(review__isnull = False)
    customer = Customer.objects.get(user_id=request.user.id)
    return render(request, 'customer_templates/order.html', {'order':order, 'form':form, 'reviewed_items':reviewed_items, 'customer':customer})

@login_required
@customer_required
def checkout(request):
  customer = Customer.objects.get(user_id=request.user.id)
  shopping_cart = ShoppingCart.objects.get(customer=customer)
  order_name = request.user.first_name + " " + request.user.last_name
  order_cook = Cook.objects.get(id=shopping_cart.cook_id)
  cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
  order = Order.objects.create( #create new pending order
    name = order_name,
    cook = order_cook,
    customer = customer,
    status = 'p',
    total = shopping_cart.total
  )
  order.save()
  for item in cart_items: #for each CartItem in shopping cart
    dish = Dish.objects.get(id=item.dish_id)
    order_item = Item.objects.create( #create an Item for order with stuff from shopping cart
      dish = dish,
      quantity = item.quantity,
      subtotal = item.subtotal,
      order = order
    )
    order_item.save()
    item.delete() #delete item from CartItem
  shopping_cart.empty = True #set shopping cart back to empty
  shopping_cart.total = 0 #clear total for shopping cart
  shopping_cart.save()
  return HttpResponseRedirect(reverse('customer_home'))

#get the distance between origin and destination using google maps api
def get_distance(origin, destination):
  req = urllib.request.Request('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + origin + '&destinations=' + destination + '&key=AIzaSyCPqdytEpfi1zIU4dj8B3KddX8-b6OPJoM')
  resp_json = urllib.request.urlopen(req, context=ssl.SSLContext()).read().decode('utf-8')
  resp = json.loads(resp_json)
  return resp['rows'][0]['elements'][0]['distance']['text'].strip(' mi')

#find nearby cooks by checking the distance between customer and all cooks, filtering on 
#delivery distance set by cook
def find_nearby_cooks(request):
  customer = get_object_or_404(Customer, user_id=request.user.id)
  cooks = Cook.objects.all()
  cook_addresses = Address.objects.filter(is_cook_address=True)
  customer_address = Address.objects.get(customer=customer)
  formatted_cook_addresses = []
  formatted_customer_address = customer_address.street_name.replace(" ", "+") + "+" + customer_address.city + "+" + customer_address.state #format the customer address as a url parameter
  distance_cooks = []
  nearby_cooks = []
  for address in cook_addresses:
    add_str = address.street_name #format the cook_address as a url parameter
    add_str = add_str.replace(" ", "+")
    add_str = add_str + "+" + address.city + "+" + address.state
    tup = (add_str, address.cook_id)
    formatted_cook_addresses.append(tup)
  for add in formatted_cook_addresses:
    distance_cook = (get_distance(add[0], formatted_customer_address), add[1])
    distance_cooks.append(distance_cook)
  for distance in distance_cooks:
    cook = Cook.objects.get(id=distance[1])
    dist = distance[0].replace(",","")
    if float(dist) < cook.delivery_distance_miles:
      nearby_cooks.append(cook)
  return nearby_cooks #returning a queryset of cooks

#use find_nearby_cooks to find all nearby dishes
def find_nearby_dishes(request):
  cooks = find_nearby_cooks(request)
  dishes = Dish.objects.filter(cook__in=cooks)
  return dishes #returning a queryset of dishes

'''
Allows the customer to edit their username, password, and phone number.
The form will show the customer their username, but they will not be allowed to edit it.
'''
def customer_edit_profile(request):
  current_user = models.User.objects.get(id=request.user.id)
  if request.method == 'POST':
    form = UserEditForm(request.POST, 
      request.FILES, 
      instance=request.user)
    if request.POST['first_name'] == "":
      request.POST['first_name'] = request.user.first_name
    phone_form = PhoneEditForm(request.POST,
      request.FILES,
      instance = request.user.customer)
    if form.is_valid() and phone_form.is_valid():
      data = form.cleaned_data
      phone_data = form.cleaned_data
      form.save()
      phone_form.save()
      return HttpResponseRedirect(reverse('customer_home'))
  else:
    current_user.email = request.user.username
    form = UserEditForm(instance=request.user)
    phone_form = PhoneEditForm(instance=request.user.customer)
    context = {
      'phone_form': phone_form,
      'form': form,
    }
    return render(request,'customer_templates/customer_edit_profile.html', context)

@login_required
@customer_required
def favorites(request):
  customer = Customer.objects.get(user_id=request.user.id)
  favorite_dishes = customer.favorites.all()
  context = {
    'customer': customer,
    'dishes': favorite_dishes
  }
  return render(request, 'customer_templates/favorites.html', context)

    