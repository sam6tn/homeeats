from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django import forms
from .models import Cuisine
from .models import Customer
from .models import Cook
from .models import Dish


'''
Information the customer needs to enter to create an account
'''
class CustomerCreateForm(forms.ModelForm):
    
    first_name = forms.CharField(label='First Name',required=True,
    error_messages={'required':'Please enter your first name.'},)
    last_name = forms.CharField(label='Last Name', required=True,error_messages={'required':'Please enter your last name.'})
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True,)
    street = forms.CharField(required=True,label='Street Address')
    town = forms.CharField(required=True,label='City/Town')
    state = forms.CharField(required=True,)
    zipcode = forms.CharField(required=True,)
    phone_number = forms.CharField(label='Phone Number')
    
    class Meta:
        model = Customer 
        fields = ('first_name','last_name','password','email','street','town','state',
        'zipcode','phone_number')


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

class CookCreateForm(forms.ModelForm):
    kitchen_license = forms.CharField(label='Kitchen License')
    phone_number = forms.CharField(label='Phone Number')
    
    class Meta:
      model = User
      fields = ['first_name', 'last_name', 'email', 'password']

class DishSearchForm(forms.Form):
    search = forms.CharField(label="Search",max_length=30, required=False)
    SORT_CHOICES = (
        ('none', '(no selection)'),
        ('rating', 'Rating'),
        ('price', 'Price: Low to High'),
        ('reverse_price', 'Price: High to Low'),
        ('distance', 'Distance'),
    )
    cuisine_types = Cuisine.objects.all()
    cuisines = [('none','(no selection)')]
    for cuisine in cuisine_types:
        cuisines.append((cuisine.id,cuisine.name))
    sort = forms.ChoiceField(choices=SORT_CHOICES, widget=forms.Select, required=False)
    cuisine = forms.ChoiceField(choices=cuisines, widget=forms.Select, required=False)

