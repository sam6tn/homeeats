from django import forms
from .models import Cook

class CookCreateForm(forms.ModelForm):
    class Meta:
      model = Cook
      fields = ['first_name', 'last_name', 'email', 'password'] 
