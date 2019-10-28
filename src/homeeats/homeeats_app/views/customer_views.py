from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.template import loader
from ..forms import CustomerCreateForm
from .. import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from ..models import Dish, Customer
from .. import models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

'''
Homepage view before login
'''

@login_required
def dish(request, dish_id):
    try:
      customer = Customer.objects.get(user_id=request.user.id)
    except Exception as e:
      return redirect('/')
    dish = Dish.objects.get(id=dish_id) #get Dish object from dish_id
    reviews = dish.dish_review_set.all() #get all reviews for that Dish
    return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews':reviews})

@login_required
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