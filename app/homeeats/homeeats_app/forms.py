from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User


class CustomerForm(forms.ModelForm):
    
    first_name = forms.CharField(label='First Name',required=True,
        error_messages={'required':'Please enter your first name.'},)
    last_name = forms.CharField(label='Last Name', required=True,error_messages={'required':'Please enter your last name.'})
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True,)
    address = forms.CharField(required=True,)
    
    class Meta:
        model = Customer 
        fields = ('first_name','last_name','password','email','address',)