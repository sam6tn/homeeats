from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.models import User
from .models import Cook
from .models import Customer

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
