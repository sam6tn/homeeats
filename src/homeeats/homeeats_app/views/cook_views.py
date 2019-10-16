from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from .. import forms
from .. import models
from django.shortcuts import render
from django.urls import reverse

def create(request):
  if request.method == 'POST':
    cook_create_form = forms.CookCreateForm(request.POST)
    if cook_create_form.is_valid():
      data = cook_create_form.cleaned_data
      user = User.objects.create_user(username=data['email'], password=data['password'])
      cook = models.Cook.objects.create(
        first_name=data['first_name'],
        last_name=data['last_name'],
        kitchen_license=data['kitchen_license'],
        phone_number=data['phone_number'],
        user_id=user.id
      )
      user.has_perm('cook')
      user.save()
      cook.save()
      return HttpResponseRedirect(reverse('cook_login'))
    else:
      return render(request, 'cook_templates/cook_create.html', {'cook_create_form': cook_create_form})
  else:
    cook_create_form = forms.CookCreateForm()
    return render(request, 'cook_templates/cook_create.html', {'cook_create_form': cook_create_form})

def login(request):
  return HttpResponse("cook_login")
