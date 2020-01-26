from django.db import models
from django.contrib.postgres.fields import ArrayField
from django import forms
from .models import User, Cuisine, Customer, Cook, Dish, Dish_Review, Address
from phonenumber_field.modelfields import PhoneNumberField




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
        #fields = ('first_name','last_name','password','email','street','town','state',
         #   'zipcode','phone_number',)
        fields = ('first_name','last_name','password','phone_number',)
    
class AddressCreateForm(forms.ModelForm):
    street = forms.CharField(required=True,label='Street Address')
    town = forms.CharField(required=True,label='City/Town')
    state = forms.CharField(required=True,)
    zipcode = forms.CharField(required=True,)

    class Meta:
        model = Address
        fields = ('street', 'town', 'state', 'zipcode',)

class AddressEditForm(forms.ModelForm):
    street = forms.CharField(required=True,label='Street Address')
    town = forms.CharField(required=True,label='City/Town')
    state = forms.CharField(required=True,)
    zipcode = forms.CharField(required=True,)

    class Meta:
        model = Address
        fields = ('street', 'town', 'state', 'zipcode',)


class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(label='First Name',required=True,
    error_messages={'required':'Please enter your first name.'},)
    last_name = forms.CharField(label='Last Name', required=True,error_messages={'required':'Please enter your last name.'})
    username = forms.CharField(label='Email',widget=forms.TextInput(attrs={'readonly':'readonly'}))
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')

class PhoneEditForm(forms.ModelForm):
    #phone_number = forms.CharField(label='Phone Number')
    phone_number = PhoneNumberField(help_text='Please enter a valid phone number')
    class Meta:
        model = Customer
        fields = ('phone_number',)
    
    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        if not data.isdigit():
            raise forms.ValidationError('Enter a valid phone number, e.g. 0123456789')
            
        return data

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

class CookCreateForm(forms.ModelForm):
    kitchen_license = forms.CharField(label='Kitchen License')
    phone_number = forms.CharField(label='Phone Number')
    delivery_distance_miles = forms.IntegerField(label='Maximum Delivery Distance (miles)')
    delivery_fee = forms.DecimalField(label='Delivery Fee', decimal_places=2, max_digits=6)
    street = forms.CharField(required=True,label='Street Address')
    town = forms.CharField(required=True,label='City/Town')
    state = forms.CharField(required=True,)
    zipcode = forms.CharField(required=True,)
    government_id = forms.ImageField()
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
      model = User
      fields = ['first_name', 'last_name', 'email', 'password']
    
class DishCreateForm(forms.Form):
    title = forms.CharField(required=True,)
    #cuisine = forms.ModelChoiceField(queryset=Cuisine.objects.all())
    description = forms.CharField(required=True,)
    ingredients = forms.CharField()
    dish_image = forms.ImageField()
    cook_time = forms.IntegerField(required=True,)
    #cook = forms.ModelChoiceField(queryset=Cook.objects.all())
class DishEditForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ('title', 'description','ingredients', 'dish_image', 'cook_time', 'cuisine', 'vegan', 'allergies')

class DishSearchForm(forms.Form):
    search = forms.CharField(label="Search",max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder':'Search','class':'form-control mr-sm-2'}))
    SORT_CHOICES = (
        ('rating', 'Sort: Rating'),
        ('price', 'Price: Low to High'),
        ('reverse_price', 'Price: High to Low'),
    )
    cuisine_types = Cuisine.objects.all()
    cuisines = [('none','Cuisine: All')]
    for cuisine in cuisine_types:
        cuisines.append((cuisine.id,'Cuisine: '+cuisine.name))
    sort = forms.ChoiceField(
        choices=SORT_CHOICES, 
        widget=forms.Select(attrs={'onchange':'submitForm()','class':'custom-select','style':'font-size:10pt;margin-right:10px'}), 
        required=False)
    cuisine = forms.ChoiceField(
        choices=cuisines, 
        widget=forms.Select(attrs={'onchange':'submitForm()','class':'custom-select','style':'font-size:10pt;margin-right:10px'}), 
        required=False)

class DishReviewForm(forms.ModelForm):
    #dish_rating = forms.IntegerField(widget=forms.TextInput(attrs={'readonly':'readonly','size':1}))
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'rows': 3, 'placeholder':'Write your review here!'}))
    class Meta:
        model = Dish_Review
        #fields = ('dish_rating', 'description')
        fields = ('description',)

class DishCreateForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ('title', 'cuisine', 'description', 'dish_image', 'ingredients', 'cook_time', 'price', 'vegan', 'allergies')
