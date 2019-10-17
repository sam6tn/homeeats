from ..views import customer_views
from django.urls import path

urlpatterns = [
  path('dish/<int:dish_id>/', customer_views.dish, name='customer_dish')
]
