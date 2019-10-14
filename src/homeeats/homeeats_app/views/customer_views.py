from django.shortcuts import render
from ..forms import CustomerCreateForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

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
  return HttpResponse("customer_login")