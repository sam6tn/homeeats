from django.shortcuts import render
from django.contrib.auth.models import User
from django.template import loader
from ..forms import CustomerCreateForm
from .. import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from ..models import Dish
from .. import models

'''
Homepage view before login
'''
def index(request):
    template = loader.get_template('../templates/index.html')
    return HttpResponse(template.render())

def dish(request, dish_id):
  dish = Dish.objects.get(id=dish_id) #get Dish object from dish_id
  reviews = dish.dish_review_set.all() #get all reviews for that Dish
  return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews':reviews})