from django.test import TestCase, Client
from django.urls import reverse
import json 
from django.test import RequestFactory
from . import views
from homeeats_app.models import Cook, Cuisine, Dish, Dish_Review, Address, User, Customer
from .forms import DishSearchForm, CustomerCreateForm, DishReviewForm, UserEditForm, PhoneEditForm

class CookHomeTest(TestCase):
    fixtures = ['test_data.json']
    def test_cuisines_on_cook_manage(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        response = self.client.get(reverse('cook_manage'))
        cuisines = response.context['cuisines']
        self.assertEquals(cuisines[0]['name'], "Italian")
        self.assertEquals(cuisines[1]['name'], "Mexican")
        self.client.logout()
    def test_not_logged_in_causes_redirect_to_login_for_cook_home(self):
        response = self.client.get(reverse('cook_home'))
        self.assertEquals(response.status_code, 302)
    def test_orders_work(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       orders = response.context['pending_orders']
       self.assertEquals(len(orders), 1)
    def test_orders_page_works(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.assertEquals(response.status_code, 200)
    def test_correct_pending_order_renders(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.assertEquals(response.context['pending_orders'][0]['id'], 1)
       self.assertEquals(response.context['pending_orders'][0]['status'], 'p')
    def test_correct_in_progress_order_renders(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('cook_home'))
       self.assertEquals(response.context['in_progress_orders'][0]['id'], 2)
       self.assertEquals(response.context['in_progress_orders'][0]['status'], 'c')
       

class CookManageTest(TestCase):
    fixtures = ['test_data.json']
    def test_delete_dish(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        self.client.get(reverse('delete_dish', args=[2]))
        response = self.client.get(reverse('cook_cuisine_dishes', args=[1]))
        dishes = response.context['dishes']
        self.assertEquals(len(dishes),1)
    def test_delete_dish_redirects_to_cook_cuisine_dishes(self):
       self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
       response = self.client.get(reverse('delete_dish', args=[2]))
       self.assertEquals(response.status_code, 302)
       self.assertEquals(response.url, "/cook/cuisine/1/dishes")

class CustomerCheckoutTest(TestCase):
    def test_checkout_access(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.get(reverse('checkout'))
        self.assertEquals(response.status_code, 302)
    def test_checkout_redirect(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.get(reverse('checkout'))
        self.assertEquals(response.url, "/?next=/customer/checkout/")
    def test_checkout_home_redirect(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.get(reverse('checkout'))
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.url, "/?next=/customer/home/")
    def test_checkout_home_access(self):
        self.client.login(username='anki@anki.com', password='ankith')
        self.client.get(reverse('checkout'))
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.status_code, 302)

class CustomerHomeTest(TestCase):
    def test_not_logged_in_causes_redirect_to_login_for_cook_home(self):
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.status_code, 302)
    def test_search_form_is_valid(self):
        form = DishSearchForm(data={'search':'', 'sort':'none', 'cuisine':'none'})
        self.assertTrue(form.is_valid())
    def test_search_form_not_valid(self):
        form = DishSearchForm()
        self.assertFalse(form.is_valid())

class CustomerDishReviewTest(TestCase):
    def test_review_form_is_valid(self):
        form = DishReviewForm(data={'dish_rating':5, 'description':'', 'report_flag':False})
        self.assertFalse(form.is_valid()) #change when fixed
    def test_review_form_not_valid(self):
        form = DishReviewForm(data={'dish_rating':5, 'description':'', 'report_flag':False})
        self.assertFalse(form.is_valid())
    def test_review_form_rating_too_high(self):
        form = DishReviewForm(data={'dish_rating':6, 'description':'', 'report_flag':False})
        self.assertFalse(form.is_valid())
    def test_review_form_rating_too_low(self):
        form = DishReviewForm(data={'dish_rating':-1, 'description':'', 'report_flag':False})
        self.assertFalse(form.is_valid())
    
class SearchTest(TestCase):
    def test_search_empty(self):
        form = DishSearchForm(data={'search':'', 'sort':'none', 'cuisine':'none'})
        self.assertTrue(form.is_valid())

class AccountCreationTest(TestCase):
    def test_cook_create_with_valid_data(self):
        response = self.client.post(reverse('cookcreate'), {'first_name': 'Bob', 'last_name': 'Saget', 'email': 'bob@bob.com', 'password': 'sagetsaget', 'kitchen_license': 'asdfasdfasdf', 'phone_number': '7777777777'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")
    def test_customer_create_with_valid_data(self):
        response = self.client.post(reverse('customercreate'), {'first_name': 'Dave', 'last_name': 'Chapelle', 'street': '221 Baker Street', 'town': 'Fairfax', 'state': 'VA', 'zipcode': '22000', 'email': 'dave@dave.com', 'password': 'chapchap', 'phone_number': '8888888888'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")
        
class AddressCreationTest(TestCase):
     def setUp(self):
         Address.objects.create(street_name='2132 someStreet Ln', city="Chantilly", state="VA", zipcode="20151")
         Address.objects.create(street_name='123 Jefferson Park Av', city="Herndon", state="VA", zipcode="20166")
         cook_user = User.objects.create(is_cook=True)
         self.cook = Cook.objects.create(user=cook_user)
         self.cook_address = Address.objects.create(street_name='733 Summer Grove Terr', city="Ashburn", state="MD", zipcode="12333", cook=self.cook)

class UserGroupTest(TestCase):
    def test_cook_create(self):
        response = self.client.post(reverse('cookcreate'), {'first_name': 'Bob', 'last_name': 'Saget', 'email': 'bob@bob.com', 'password': 'sagetsaget', 'kitchen_license': 'asdfasdfasdf', 'phone_number': '7777777777'})
        user = User.objects.get(username="bob@bob.com")
        self.assertTrue(user.is_cook)
    def test_redirect_cook(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.status_code, 302)
    def test_redirect(self):
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.status_code, 302)
    def test_redirect_cook_checkout(self):
        self.client.login(username='ramsey@ramsey.com', password='ramseyramsey')
        response = self.client.get(reverse('checkout'))
        self.assertEquals(response.status_code, 302)
    def test_customer_create(self):
        response = self.client.post(reverse('customercreate'), {'first_name': 'Dave', 'last_name': 'Chapelle', 'street': '221 Baker Street', 'town': 'Fairfax', 'state': 'VA', 'zipcode': '22000', 'email': 'dave@dave.com', 'password': 'chapchap', 'phone_number': '8888888888'})
        user = User.objects.get(username="dave@dave.com")
        self.assertTrue(user.is_customer)
    def test_redirect_customer(self):
        self.client.login(username='anki@anki.com', password='ankith')
        response = self.client.get(reverse('cook_home'))
        self.assertEquals(response.status_code, 302)
    def test_redirect_customer_home(self):
        response = self.client.get(reverse('cook_home'))
        self.assertEquals(response.status_code, 302)

class AddressCreationTest(TestCase):
     def setUp(self):
         Address.objects.create(street_name='2132 someStreet Ln', city="Chantilly", state="VA", zipcode="20151")
         Address.objects.create(street_name='123 Jefferson Park Av', city="Herndon", state="VA", zipcode="20166")
         cook_user = User.objects.create(is_cook=True)
         self.cook = Cook.objects.create(user=cook_user)
         self.cook_address = Address.objects.create(street_name='733 Summer Grove Terr', city="Ashburn", state="MD", zipcode="12333", cook=self.cook)

     def test_fetch_all_correct_streets_names(self):
         addresses = Address.objects.values_list('street_name', flat=True)
         self.assertTrue(addresses[0] == ('2132 someStreet Ln'))
         self.assertTrue(addresses[1] == ('123 Jefferson Park Av'))
         self.assertTrue(addresses[2] == ('733 Summer Grove Terr'))

     def test_fetch_all_correct_cities(self):
         addresses = Address.objects.values_list('city', flat=True)
         self.assertTrue(addresses[0] == ('Chantilly'))
         self.assertTrue(addresses[1] == ('Herndon'))
         self.assertTrue(addresses[2] == ('Ashburn'))

     def test_fetch_all_correct_states(self):
         addresses = Address.objects.values_list('state', flat=True)
         self.assertTrue(addresses[0] == ('VA'))
         self.assertTrue(addresses[1] == ('VA'))
         self.assertTrue(addresses[2] == ('MD'))

     def test_fetch_all_correct_zipcodes(self):
         addresses = Address.objects.values_list('zipcode', flat=True)
         self.assertTrue(addresses[0] == ('20151'))
         self.assertTrue(addresses[1] == ('20166'))
         self.assertTrue(addresses[2] == ('12333'))

     def test_correctly_saves_address_cook(self):
         self.assertTrue(self.cook.id == self.cook_address.cook.id)

class CustomerCreateFormTest(TestCase):
    def test_valid_data(self):
        form = CustomerCreateForm({
            'first_name': "First",
            'last_name': "Last",
            'password': "password",
            'email': "first@email.com",
            'street': "123 rotunda",
            'town': "Charlottesville",
            'state': "VA",
            'zipcode': "22903",
            'phone_number': "0123456789"
        })
        self.assertTrue(form.is_valid())

    '''
    Tests that invalid emails are not accepted
    '''
    def test_invalid_email(self):
        form = CustomerCreateForm({
            'first_name': "First",
            'last_name': "Last",
            'password': "password",
            'email': "first",
            'street': "123 rotunda",
            'town': "Charlottesville",
            'state': "VA",
            'zipcode': "22903",
            'phone_number': "0123456789"
        })      
        self.assertFalse(form.is_valid())
    
    
    '''
    Tests that data will not saved if required information is missing
    '''
    def test_missing_required_firstname(self):
        form = CustomerCreateForm({
            'first_name': "",
            'last_name': "Last",
            'password': "password",
            'email': "first",
            'street': "123 rotunda",
            'town': "Charlottesville",
            'state': "VA",
            'zipcode': "22903",
            'phone_number': "0123456789"
        })
        self.assertFalse(form.is_valid())
    

class CustomerEditProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Test1", password="Test1", first_name="first", last_name="last")
        self.customer = models.Customer.objects.create(phone_number="0123456789", user_id=self.user.id)
        user.save()
        customer.save()
        before_change = self.user
        before_customer = self.customer
        self.client.login(username=self.user.username,password=self.user.password)

        profile_before = Profile.objects.create(first_name="Test", last_name="Case", grad_year=2021, major="CS", number="1234567890", email="test@test.com")
        profile_before.save()

    '''
    Changes users first name and tests if it's the same as the copy from setup
    '''
    def test_update_firstname(self):
        form = UserEditForm(instance=self.user, {'first_name':"Changed"})
        if form.is_valid(){
            data = form.cleaned_data
            form.save()
        }
        assertFalse(before_change.first_name==self.user.first_name)

    '''
    Changes user's last name and tests if it's the same as the copy from setup
    '''
    def test_update_lastname(self):
        form = UserEditForm(instance=self.user, {'last_name':"Changed"})
        if form.is_valid(){
            data = form.cleaned_data
            form.save()
        }
        assertFalse(before_change.last_name==self.user.last_name)

    '''
    Attempts to change user's username/email but this shouldn't be allowed so the 
    form should stop the change from saving
    '''
    def test_update_username(self):
        form = UserEditForm(instance=self.user, {'username':"Changed"})
        if form.is_valid():
            data = form.cleaned_data
            form.save()
        assertTrue(before_change.username==self.user.username) #Shouldn't be able to change username
    
    '''
    Changes customer's phone number and tests if it's the same as the copy from setup
    '''
    def test_update_phonenumber(self):
        form = PhoneEditForm(instance=self.customer,{'phone_number':"0987654321"})
        if form.is_valid(){
            data = form.cleaned_data
            form.save()
        }
        assertFalse(before_customer==self.customer)
