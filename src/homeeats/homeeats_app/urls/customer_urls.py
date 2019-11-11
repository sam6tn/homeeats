from ..views import customer_views
from django.urls import path

urlpatterns = [
  path('dish/<int:dish_id>/', customer_views.dish, name='customer_dish'), #url for dish detailed page
  path('home/', customer_views.home, name='customer_home'), #customer landing page
  path('editprofile/', customer_views.customer_edit_profile, name='customer_edit_profile'),
]
