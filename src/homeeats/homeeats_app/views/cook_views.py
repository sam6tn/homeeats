from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from .. import forms
from ..models import Cook, Cuisine, Dish
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.forms import model_to_dict
from django.contrib.auth.decorators import login_required


#cook home page after login
@login_required
def home(request): 
  cuisines = get_cuisines_by_cook(request)
  context = {  #pass in context
    'cuisines': cuisines
  }
  return render(request, 'cook_templates/cook_home.html', context)

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


