from django.test import TestCase, Client
from django.urls import reverse
import json 
from django.test import RequestFactory
from . import views
from django.contrib.auth.models import User
from homeeats_app.models import Cook, Cuisine, Dish, Dish_Review

class CookHomeTest(TestCase):
    fixtures = ['test_data.json']
    def test_cuisines_on_cook_home(self):
        self.client.login(username='ramsey', password='ramseyramsey')
        response = self.client.get(reverse('cook_home'))
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

class AccountCreationTest(TestCase):
    def test_cook_create_with_valid_data(self):
        response = self.client.post(reverse('cookcreate'), {'first_name': 'Bob', 'last_name': 'Saget', 'email': 'bob@bob.com', 'password': 'sagetsaget', 'kitchen_license': 'asdfasdfasdf', 'phone_number': '7777777777'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")
    def test_customer_create_with_valid_data(self):
        response = self.client.post(reverse('customercreate'), {'first_name': 'Dave', 'last_name': 'Chapelle', 'street': '221 Baker Street', 'town': 'Fairfax', 'state': 'VA', 'zipcode': '22000', 'email': 'dave@dave.com', 'password': 'chapchap', 'phone_number': '8888888888'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")
    

    


