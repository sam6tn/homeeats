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


