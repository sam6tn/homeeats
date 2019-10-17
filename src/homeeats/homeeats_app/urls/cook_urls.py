from ..views import cook_views
from django.urls import path

urlpatterns = [
  path('create/', cook_views.create, name='cook_create'),
  path('get/', cook_views.get, name='cook_get'),
  path('login/', cook_views.login, name='cook_login'),
  path('home/', cook_views.home, name='cook_home')
]