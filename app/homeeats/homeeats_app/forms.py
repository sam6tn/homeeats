from django import forms
from django.contrib.auth.models import User
from .models import Cook

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