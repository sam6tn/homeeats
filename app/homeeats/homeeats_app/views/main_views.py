from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from .. import forms
from .. import models
from django.shortcuts import render
from django.urls import reverse
from django.template import loader

def index(request):
    template = loader.get_template('../templates/index.html')
    return HttpResponse(template.render())

def signup(request):
  if request.method == 'POST':
    form = forms.RegisterForm(request.POST)
    if form.is_valid():
      data = form.cleaned_data
      user = User.objects.create_user(username=data['username'], password=data['password'])
      customer = models.Customer.objects.create(first_name=data['first_name'], last_name=data['last_name'], user_id=user.id)
      user.save()
      customer.save()
      return HttpResponse('ok')
    else:
      return render(request, 'customer_templates/customer_signup.html', {'userForm': form})
  else:
    cookForm = forms.CookCreateForm()
    userForm = forms.UserForm()
    return render(request, 'cook_templates/cook_create.html', {'cookForm': cookForm, 'userForm': userForm})