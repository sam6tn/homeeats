from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.models import User
from .models import Cook
from .models import Customer

class CustomerCreateForm(forms.ModelForm):
    
    first_name = forms.CharField(label='First Name',required=True,
        error_messages={'required':'Please enter your first name.'},)
    last_name = forms.CharField(label='Last Name', required=True,error_messages={'required':'Please enter your last name.'})
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True,)
    address = forms.CharField(required=True,)
    
    class Meta:
        model = Customer 
        fields = ('first_name','last_name','password','email','address',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

class CookCreateForm(forms.ModelForm):
    class Meta:
      model = Cook
      fields = ['first_name', 'last_name']

class RegisterForm(forms.ModelForm):
  first_name = forms.CharField()
  last_name = forms.CharField()
  class Meta:
    model = User
    fields = ('username','password')