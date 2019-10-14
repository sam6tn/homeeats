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
      cook = models.Cook.objects.create(first_name=data['first_name'], last_name=data['last_name'], user_id=user.id)
      user.has_perm('cook')
      user.save()
      cook.save()
      return HttpResponseRedirect(reverse('cook_login'))
    else:
      return render(request, 'cook_templates/cook_create.html', {'userForm': form})
  else:
    userForm = forms.RegisterForm()
    return render(request, 'cook_templates/cook_create.html', {'userForm': userForm})

def login(request):
  return HttpResponse("cook_login")