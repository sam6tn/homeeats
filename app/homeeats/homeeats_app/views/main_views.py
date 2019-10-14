from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from .. import forms
from .. import models
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages

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
      user.has_perm('customer')
      user.save()
      customer.save()
      return HttpResponse('ok')
    else:
      return render(request, 'customer_templates/customer_signup.html', {'userForm': form})
  else:
    userForm = forms.RegisterForm()
    return render(request, 'customer_templates/customer_signup.html', {'userForm': userForm})

def userLogin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    
    form = AuthenticationForm()
    return render(request = request, template_name = "../templates/login.html", context={"form":form})