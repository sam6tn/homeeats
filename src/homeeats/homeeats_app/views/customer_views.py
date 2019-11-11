from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.template import loader
from ..forms import CustomerCreateForm, DishReviewForm, UserEditForm, AddressEditForm, PhoneEditForm
from .. import forms
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from ..models import Dish, Customer, Dish_Review, Cook, Address
from .. import models
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

@login_required
@customer_required
def dish(request, dish_id):
    dish = Dish.objects.get(id=dish_id) #get Dish object from dish_id
    reviews = dish.dish_review_set.all() #get all reviews for that Dish
    if request.method == "POST":
      if "review_submit" in request.POST:
        form = DishReviewForm(request.POST)
        if form.is_valid():
          data = form.cleaned_data
          rating = data["dish_rating"]
          text = data["description"]
          report = data["report_flag"]
          customer = Customer.objects.get(user_id=request.user.id)

          #save the new review
          dr = Dish_Review(dish_rating=rating,description=text,report_flag=report,customer=customer,dish=dish)
          dr.save()

          #calculate new dish rating
          all_dish_reviews = Dish_Review.objects.filter(dish=dish)
          total_rating = 0
          for review in all_dish_reviews:
            total_rating += review.dish_rating
          new_rating = int(round(total_rating/len(all_dish_reviews)))
          dish.rating = new_rating
          print(dish.rating)
          dish.save()

        return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews':reviews, 'form':form})
        

      elif "add_to_order" in request.POST:
        print("Do add dish to order logic here")

    else:
      try:
        customer = Customer.objects.get(user_id=request.user.id)
      except Exception as e:
        return redirect('/')
      form = DishReviewForm()
      return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews':reviews, 'form':form})

@login_required
@customer_required
def checkout(request):
  return render(request, 'customer_templates/checkout.html')

@login_required
@customer_required
def home(request):
    try:
      customer = Customer.objects.get(user_id=request.user.id)
    except Exception as e:
      return redirect('/')
    if request.method == 'POST':
      form = forms.DishSearchForm(request.POST)
      if form.is_valid():
        data = form.cleaned_data
        search = data['search']
        sort = data['sort']
        cuisine = data['cuisine']
        dishes = Dish.objects.filter(title__icontains=search)

        if (cuisine != 'none'):
          dishes = dishes.filter(cuisine=cuisine)

        if (sort == 'rating'):
          dishes = dishes.order_by('-rating')
        elif (sort == 'price'):
          dishes = dishes.order_by('price')
        elif (sort == 'reverse_price'):
          dishes = dishes.order_by('-price')

        return render(request, 'customer_templates/customer_home.html', {'dishes':dishes, 'form': form})
      else:
        dishes = Dish.objects.all()
        return render(request, 'customer_templates/customer_home.html', {'dishes': dishes, 'form': form})

    else:
      form = forms.DishSearchForm()
      dishes = Dish.objects.all()
      return render(request, 'customer_templates/customer_home.html', {'dishes': dishes, 'form':form})

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
    if float(distance[0]) < cook.delivery_distance_miles:
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
    

  
