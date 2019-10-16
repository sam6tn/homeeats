from django.shortcuts import render
from ..forms import CustomerCreateForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from ..models import Dish

def create(request):
  if request.method == 'POST':
    form = CustomerCreateForm(request.POST)
    if form.is_valid():
        cook = form.save(commit=False)
        cook.save()
        return HttpResponseRedirect(reverse('customer_login'))
  else:
    form = CustomerCreateForm()
    return render(request, 'customer_templates/customer_create.html', {'form': form})

def login(request):
  return render(request, 'login.html')

def dish(request, dish_id):
  dish = Dish.objects.get(id=dish_id)
  reviews = dish.dish_review_set.all()
  return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews':reviews})