from ..views import cook_views
from django.urls import path

urlpatterns = [
  path('home/', cook_views.home, name='cook_home')
]
