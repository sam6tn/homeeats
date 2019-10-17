from ..views import main_views as main
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
  path('', main.index, name='index'),
  path('login', main.userLogin, name='userLogin'),
]