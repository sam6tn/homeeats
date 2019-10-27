from ..views import cook_views
from django.urls import path

urlpatterns = [
  path('home/', cook_views.home, name='cook_home'),
  path('cuisines/', cook_views.get_cuisines_by_cook, name='cook_cuisines')
]
