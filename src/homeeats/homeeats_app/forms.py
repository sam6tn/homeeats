from django.db import models
from django.contrib.postgres.fields import ArrayField
from django import forms
from .models import User, Cuisine, Customer, Cook, Dish, Dish_Review, Address
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone

def getYear():
    return timezone.localtime(timezone.now()).year

class DatePickerForm(forms.Form):

    #Calculate which years to display for date picker
    years=[]
    current_year = getYear()
    num_years_passed = current_year - 2019
    for i in range(0,num_years_passed+1):
        years.append(2019+i)

    start_date = forms.DateField(widget=forms.SelectDateWidget(years=years))
    end_date = forms.DateField(widget=forms.SelectDateWidget(years=years))

'''
Information the customer needs to enter to create an account
'''
class CustomerCreateForm(forms.ModelForm):
    error_css_class = 'error'
    first_name = forms.CharField(label='First Name',required=True,
    error_messages={'required':'Please enter your first name.'},)
    last_name = forms.CharField(label='Last Name', required=True,error_messages={'required':'Please enter your last name.'})
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(required=True,)
    #street = forms.CharField(required=True,label='Street Address')
    #town = forms.CharField(required=True,label='City/Town')
    #state = forms.CharField(required=True,)
    #zipcode = forms.CharField(required=True,)
    phone_number = forms.CharField(label='Phone Number')
    
    class Meta:
        model = Customer 
        #fields = ('first_name','last_name','password','email','street','town','state',
         #   'zipcode','phone_number',)
        fields = ('first_name','last_name','password','phone_number',)
    
    def clean_phone_number(self):
        data = self.cleaned_data['phone_number']
        if not data.isdigit():
            raise forms.ValidationError('Enter a valid phone number, e.g. 0123456789')
            
        return data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            #messages.add_message(request, messages.ERROR, 'An account with this email already exists, go to login page or use a different email')
            #return render(request, 'customer_create.html', {'form': form})
            raise forms.ValidationError("An account with this email already exists, go to login page or use a different email")
        return email    

class AddressCreateForm(forms.ModelForm):
    street = forms.CharField(required=True,label='Street Address')
    town = forms.CharField(required=True,label='City/Town')
    state = forms.CharField(required=True,)
    zipcode = forms.CharField(required=True,)

    class Meta:
        model = Address
        fields = ('street', 'town', 'state', 'zipcode',)

    def clean_zipcode(self):
        zipcode = self.cleaned_data.get('zipcode')
        if not zipcode.isdigit():
            raise forms.ValidationError("Zipcode must be all digits.")
        return zipcode
    
    def __init__(self, *args, **kwargs):
        super(AddressCreateForm, self).__init__(*args, **kwargs)

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
    
    phone_number = PhoneNumberField(help_text='Please enter a valid phone number')

    class Meta:
        model = Customer
        fields = ('phone_number',)
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(str(phone_number)) != 10:
            raise forms.ValidationError('Enter a valid 10-digit phone number, e.g. 0123456789')
            
        return phone_number


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

class CookCreateForm(forms.ModelForm):
    kitchen_license = forms.CharField(required=True, label='Kitchen License')
    phone_number = forms.CharField(required=True, label='Phone Number')
    delivery_distance_miles = forms.IntegerField(required=True, label='Maximum Delivery Distance (miles)')
    delivery_fee = forms.DecimalField(required=True, label='Delivery Fee', decimal_places=2, max_digits=6)
    street = forms.CharField(required=True, label='Street Address')
    town = forms.CharField(required=True,label='City/Town')
    state = forms.CharField(required=True,)
    zipcode = forms.CharField(required=True,)
    government_id = forms.ImageField(required=True,)
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
      model = User
      fields = ['first_name', 'last_name', 'email', 'password']
    
    '''
    Raising validation errors if a phone number is the incorrect length or contains letters
    '''
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(str(phone_number)) != 10:
            raise forms.ValidationError('Enter a valid 10-digit phone number, e.g. 0123456789')
            
        return phone_number

    '''
    Raising validation errors if a zipcode is invalid
    '''
    def clean_zipcode(self):
        zipcode = self.cleaned_data.get('zipcode')
        if not zipcode.isdigit():
            raise forms.ValidationError("Zipcode must be all digits.")
        return zipcode
    
class DishCreateForm(forms.Form):
    title = forms.CharField(required=True,)
    cuisine = forms.ModelChoiceField(queryset=Cuisine.objects.all(),empty_label='Select a cuisine')
    dish_image = forms.ImageField()
    ingredients = forms.CharField(required=True,widget=forms.Textarea(attrs={'style':'width=50%;','rows':2}))
    description = forms.CharField(required=True,widget=forms.Textarea(attrs={'style':'width=50%;','rows':3}))
    cook_time = forms.IntegerField(required=True, label='Cook time (in minutes)',min_value=1)
    price = forms.FloatField(required=True,min_value=0.00, widget=forms.NumberInput(attrs={'step':0.01}))
    vegan = forms.BooleanField(required=False,initial=False)
    allergies = forms.CharField(required=False)

    class Meta:
        model = Dish
        fields = ['title', 'cuisine','description', 'dish_image','ingredients','price','cook_time','vegan','allergies']

    def clean_vegan(self):
        vegan = self.cleaned_data.get('vegan')
        if vegan == 'on':
            vegan = True
        else:
            vegan = False
        return vegan


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
        widget=forms.Select(attrs={'onchange':'submitForm()','class':'custom-select','style':'font-size:10pt;margin-right:10px',}), 
        required=False)

class DishReviewForm(forms.ModelForm):
    #dish_rating = forms.IntegerField(widget=forms.TextInput(attrs={'readonly':'readonly','size':1}))
    description = forms.CharField(widget=forms.Textarea(attrs={'cols': 50, 'rows': 3, 'placeholder':'Write your review here!'}))
    class Meta:
        model = Dish_Review
        #fields = ('dish_rating', 'description')
        fields = ('description',)
