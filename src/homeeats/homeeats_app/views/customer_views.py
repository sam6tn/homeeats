from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.template import loader
from ..forms import CustomerCreateForm, DishReviewForm
from .. import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from ..models import Dish, Customer, Dish_Review
from .. import models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from ..decorators import customer_required


'''
Homepage view before login
'''

@login_required
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
          dr = Dish_Review(dish_rating=rating,description=text,report_flag=report,customer=customer,dish=dish)
          dr.save()
          return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews':reviews, 'form':form})
        else:
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
        return render(request, 'customer_templates/customer_home.html', {'dishes':dishes, 'form': form})
      else:
        dishes = Dish.objects.all()
        return render(request, 'customer_templates/customer_home.html', {'dishes': dishes, 'form': form})

    else:
      form = forms.DishSearchForm()
      dishes = Dish.objects.all()
      return render(request, 'customer_templates/customer_home.html', {'dishes': dishes, 'form':form})