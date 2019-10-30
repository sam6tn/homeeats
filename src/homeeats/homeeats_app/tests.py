from django.test import TestCase, Client
from django.urls import reverse
import json 
from django.test import RequestFactory
from . import views
from django.contrib.auth.models import User
from homeeats_app.models import Cook, Cuisine, Dish, Dish_Review, Address, User
from .forms import DishSearchForm

class CookHomeTest(TestCase):
    fixtures = ['test_data.json']
    def test_cuisines_on_cook_home(self):
        self.client.login(username='ramsey', password='ramseyramsey')
        response = self.client.get(reverse('cook_manage'))
        cuisines = response.context['cuisines']
        self.assertEquals(cuisines[0]['name'], "Indian")
        self.assertEquals(cuisines[1]['name'], "Mexican")
        self.assertEquals(cuisines[2]['name'], "Chinese")
        self.client.logout()
    def test_not_logged_in_causes_redirect_to_login_for_cook_home(self):
        response = self.client.get(reverse('cook_home'))
        self.assertEquals(response.status_code, 302)

class CustomerHomeTest(TestCase):
    def test_not_logged_in_causes_redirect_to_login_for_cook_home(self):
        response = self.client.get(reverse('customer_home'))
        self.assertEquals(response.status_code, 302)
    def test_search_form_is_valid(self):
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

     def test_fetch_all_correct_streets_names(self):
         addresses = Address.objects.values_list('street_name', flat=True)
         self.assertTrue(addresses[0] == ('2132 someStreet Ln'));
         self.assertTrue(addresses[1] == ('123 Jefferson Park Av'));
         self.assertTrue(addresses[2] == ('733 Summer Grove Terr'));

     def test_fetch_all_correct_cities(self):
         addresses = Address.objects.values_list('city', flat=True)
         self.assertTrue(addresses[0] == ('Chantilly'));
         self.assertTrue(addresses[1] == ('Herndon'));
         self.assertTrue(addresses[2] == ('Ashburn'));

     def test_fetch_all_correct_states(self):
         addresses = Address.objects.values_list('state', flat=True)
         self.assertTrue(addresses[0] == ('VA'));
         self.assertTrue(addresses[1] == ('VA'));
         self.assertTrue(addresses[2] == ('MD'));

     def test_fetch_all_correct_zipcodes(self):
         addresses = Address.objects.values_list('zipcode', flat=True)
         self.assertTrue(addresses[0] == ('20151'));
         self.assertTrue(addresses[1] == ('20166'));
         self.assertTrue(addresses[2] == ('12333'));

     def test_correctly_saves_address_cook(self):
         self.assertTrue(self.cook.id == self.cook_address.cook.id)
