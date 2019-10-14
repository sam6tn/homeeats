from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from .. import forms
from .. import models
from django.shortcuts import render
from django.urls import reverse

def create(request):
  if request.method == 'POST':
    form = forms.RegisterForm(request.POST)
    if form.is_valid():
      data = form.cleaned_data
      user = User.objects.create_user(username=data['username'], password=data['password'])
      user.cook.first_name = data['first_name']
      user.cook.last_name = data['last_name']
      user.save()
      return HttpResponseRedirect(reverse('cook_login'))
    else:
      return render(request, 'cook_templates/cook_create.html', {'userForm': form})
  else:
    cookForm = forms.CookCreateForm()
    userForm = forms.UserForm()
    return render(request, 'cook_templates/cook_create.html', {'cookForm': cookForm, 'userForm': userForm})

def login(request):
  return HttpResponse("cook_login")
