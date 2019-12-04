from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .. import forms
from .. import models
from ..models import User, Cook, Order, Customer
from django.shortcuts import render, redirect
from django.urls import reverse
from django.template import loader
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from ..forms import CustomerCreateForm, AddressCreateForm
from django.urls import reverse_lazy

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
      user = User.objects.create_user(username=data['email'], email=data['email'], password=data['password'], first_name=data['first_name'], last_name=data['last_name'])
      customer = models.Customer.objects.create(phone_number=data['phone_number'], user_id=user.id)
      
      user.is_customer = True
      user.save()
      customer.save()
      customer = models.Customer.objects.get(user_id=user.id)
      address = models.Address.objects.create(customer=customer, street_name=data['street'], city=data['town'], state=data['state'], zipcode=data['zipcode'], current_customer_address=True)
      address.save()
      shopping_cart = models.ShoppingCart.objects.create(customer=customer)
      shopping_cart.save()
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
        delivery_distance_miles=data['delivery_distance_miles'],
        delivery_fee=data['delivery_fee'],
        user_id=user.id
      )
      user.is_cook = True
      user.save()
      cook.save()
      return HttpResponseRedirect(reverse('login'))
    else:
      return render(request, 'cook_create.html', {'cook_create_form': cook_create_form})
  else:
    cook_create_form = forms.CookCreateForm()
    return render(request, 'cook_create.html', {'cook_create_form': cook_create_form})

def logout_view(request):
  if request.user.is_cook:
    cook = Cook.objects.get(user_id=request.user.id)
    if cook.online:
      orders = Order.objects.filter(cook=cook)
      for order in orders:
        if order.status == 'p' or order.status == 'o' or order.status == 'c':
          messages.add_message(request, messages.ERROR, 'cook_online_cant_logout')
          return HttpResponseRedirect(reverse('cook_home'))   
      cook.online = False
      cook.save()
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
                try: 
                  # Gets cook based on use associated with it
                  cook = models.Cook.objects.get(user=user)
                  # If previous line dose not throw an exception then we know it is a cook
                  is_cook = True
                # Catching exception
                except models.Cook.DoesNotExist:
                  # If exception is caught then we know it is not a cook
                  is_cook = False
                # Checks if cook is approved and redirects them to the home page
                if (is_cook and cook.approved):
                  if (cook.banned):
                    messages.add_message(request, messages.ERROR, 'You are currently banned from this site, please contact an administrator')
                    return redirect('/')
                  login(request, user)
                  return redirect('/cook/home')
                # Checks if cook is not approved and redirects them back to the login page
                elif(is_cook and not cook.approved):
                  form = AuthenticationForm()
                  messages.add_message(request, messages.ERROR, 'You have not been approved yet, contact an administrator about your approval status')
                  return redirect('/')
                else:
                  # If it is not a cook then we know its a customer
                  customer = Customer.objects.get(user=user)
                  if (customer.banned):
                    messages.add_message(request, messages.ERROR, 'You are currently banned from this site, please contact an administrator')
                    return redirect('/')
                  login(request, user)
                  return redirect('/customer/home')

    form = AuthenticationForm()
    return render(request = request, template_name = "../templates/login.html", context={"form":form})

def reject_order(request):
  order = Order.objects.get(id=request.POST["order_id"])
  order.status = 'r'
  order.save()
  data={
    'success':True
  }
  return JsonResponse(data)