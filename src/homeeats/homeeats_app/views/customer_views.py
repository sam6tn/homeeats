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

'''
View of the customer creation form with form validation.
'''
def create(request):
  if request.method == 'POST':
    form = forms.CustomerCreateForm(request.POST)
    if form.is_valid():
      data = form.cleaned_data
      user = User.objects.create_user(username=data['email'], password=data['password'], first_name=data['first_name'], last_name=data['last_name'])
      customer = models.Customer.objects.create(phone_number=data['phone_number'], user_id=user.id)
      user.has_perm('customer')
      user.save()
      customer.save()
      return HttpResponse('ok')
    else:
      return render(request, 'customer_templates/customer_create.html', {'form': form})
  else:
    form = forms.CustomerCreateForm()
    return render(request, 'customer_templates/customer_create.html', {'form': form})

def dish(request, dish_id):
  dish = Dish.objects.get(id=dish_id)
  reviews = dish.dish_review_set.all()
  return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews':reviews})