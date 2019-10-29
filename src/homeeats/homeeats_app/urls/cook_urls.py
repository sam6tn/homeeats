from ..views import cook_views
from django.urls import path

urlpatterns = [
  path('home/', cook_views.home, name='cook_home'),
  path('manage/', cook_views.manage, name='cook_manage'),
  path('cuisines/', cook_views.get_cuisines_by_cook, name='cook_cuisines'),
  path('cuisine/<str:cuisine_id>/dishes', cook_views.cook_cuisine_dishes, name='cook_cuisine_dishes'),
  path('order/<str:order_id>/items', cook_views.single_order_view, name='single_order_view')
]
