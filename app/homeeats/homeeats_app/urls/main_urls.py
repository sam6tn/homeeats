from ..views import main_views as main
from django.urls import path

urlpatterns = [
  path('', main.index, name='index'),
]