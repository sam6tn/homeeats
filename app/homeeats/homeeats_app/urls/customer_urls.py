from ..views import customer_views
from django.urls import path

urlpatterns = [
  path('create/', customer_views.create, name='customer_create'),
  path('login/', customer_views.login, name='customer_login')
]
