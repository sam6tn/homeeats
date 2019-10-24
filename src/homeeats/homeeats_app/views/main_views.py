from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from .. import forms
from .. import models
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import loader
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def index(request):
    template = loader.get_template('../templates/index.html')
    return HttpResponse(template.render())

# def signup(request):
#   if request.method == 'POST':
#     form = forms.RegisterForm(request.POST)
#     if form.is_valid():
#       data = form.cleaned_data
#       user = User.objects.create_user(username=data['username'], password=data['password'])
#       customer = models.Customer.objects.create(first_name=data['first_name'], last_name=data['last_name'], user_id=user.id)
#       user.has_perm('customer')
#       user.save()
#       customer.save()
#       return HttpResponse('ok')
#     else:
#       return render(request, 'customer_templates/customer_create.html', {'userForm': form})
#   else:
#     userForm = forms.RegisterForm()
#     return render(request, 'customer_templates/customer_create.html', {'userForm': userForm})

'''
View of the customer creation form with form validation.
'''
def customercreate(request):
  if request.method == 'POST':
    form = forms.CustomerCreateForm(request.POST)
    if form.is_valid():
      data = form.cleaned_data
      user = User.objects.create_user(username=data['email'], password=data['password'], first_name=data['first_name'], last_name=data['last_name'])
      customer = models.Customer.objects.create(phone_number=data['phone_number'], user_id=user.id)
      user.has_perm('customer')
      user.save()
      customer.save()
      return HttpResponseRedirect(reverse('login'))
    else:
      return render(request, 'customer_create.html', {'form': form})
  else:
    form = forms.CustomerCreateForm()
    return render(request, 'customer_create.html', {'form': form})

def cookcreate(request):
  if request.method == 'POST':
    cook_create_form = forms.CookCreateForm(request.POST)
    if cook_create_form.is_valid():
      data = cook_create_form.cleaned_data
      user = User.objects.create_user(username=data['email'], password=data['password'], first_name=data['first_name'], last_name=data['last_name'])
      cook = models.Cook.objects.create(
        kitchen_license=data['kitchen_license'],
        phone_number=data['phone_number'],
        user_id=user.id
      )
      user.has_perm('cook')
      user.save()
      cook.save()
      return HttpResponseRedirect(reverse('login'))
    else:
      return render(request, 'cook_create.html', {'cook_create_form': cook_create_form})
  else:
    cook_create_form = forms.CookCreateForm()
    return render(request, 'cook_create.html', {'cook_create_form': cook_create_form})


def logout_view(request):
  logout(request)
  return redirect('/')

def userLogin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, "You are now logged in as {username}")
                try: #check if the user is a cook or a customer
                  models.Cook.objects.get(user=request.user)
                  is_cook = True
                except models.Cook.DoesNotExist:
                  is_cook = False
                if (is_cook):
                  return redirect('/cook/home')
                else:
                  return redirect('/customer/home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(request = request, template_name = "../templates/login.html", context={"form":form})