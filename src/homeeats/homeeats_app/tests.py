from django.test import TestCase, Client
from django.urls import reverse
import json 
from django.test import RequestFactory
from . import views
from django.contrib.auth.models import User
from homeeats_app.models import Cook, Cuisine, Dish, Dish_Review

# class CookHomeTest(TestCase):
#     fixtures = ['test_data.json']
#     def test_cuisines_by_cook(self):
#         self.client.login(username='GRamsey', password='ramseyramsey')
#         response = self.client.get('/cook/cuisines')
#         print(response)

