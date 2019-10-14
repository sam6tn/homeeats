from ..views import cook_views
from django.urls import path

urlpatterns = [
  path('create/', cook_views.create, name='cook_create'),
  path('login/', cook_views.login, name='cook_login')
]