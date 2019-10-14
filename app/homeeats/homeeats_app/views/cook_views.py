from django.http import HttpResponse, HttpResponseRedirect
from ..forms import CookCreateForm
from django.shortcuts import render
from django.urls import reverse

def create(request):
  if request.method == 'POST':
    form = CookCreateForm(request.POST)
    if form.is_valid():
        cook = form.save(commit=False)
        cook.save()
        return HttpResponseRedirect(reverse('cook_login'))
  else:
    form = CookCreateForm()
    return render(request, 'cook_templates/cook_create.html', {'form': form})

def login(request):
  return HttpResponse("cook_login")
