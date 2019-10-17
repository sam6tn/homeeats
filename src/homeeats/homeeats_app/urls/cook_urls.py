from ..views import cook_views
from django.urls import path

urlpatterns = [
  path('get/', cook_views.get, name='cook_get'),
  path('home/', cook_views.home, name='cook_home')
]
