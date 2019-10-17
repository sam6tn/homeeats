from django.shortcuts import render
from ..forms import CustomerCreateForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from ..models import Dish

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
    form = CustomerCreateForm(request.POST)
    if form.is_valid():
        customer = form.save(commit=False)
        customer.save()
        return HttpResponseRedirect(reverse('customer_login'))
  else:
    form = CustomerCreateForm()
    return render(request, 'customer_templates/customer_create.html', {'form': form})

def dish(request, dish_id):
  dish = Dish.objects.get(id=dish_id)
  reviews = dish.dish_review_set.all()
  return render(request, 'customer_templates/customer_dish.html', {'dish': dish, 'reviews':reviews})