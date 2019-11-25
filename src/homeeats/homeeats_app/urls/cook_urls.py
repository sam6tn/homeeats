from ..views import cook_views
from django.urls import path

urlpatterns = [
  path('home/', cook_views.home, name='cook_home'),
  path('manage/', cook_views.manage, name='cook_manage'),
  path('cuisines/', cook_views.get_cuisines_by_cook, name='cook_cuisines'),
  path('cuisine/<str:cuisine_id>/dishes', cook_views.cook_cuisine_dishes, name='cook_cuisine_dishes'),
  path('order/<str:order_id>/items', cook_views.single_order_view, name='single_order_view'),
  path('createdish/', cook_views.create_dish, name='create_dish'),
  path('deletedish/<str:dish_id>/', cook_views.delete_dish, name='delete_dish'),
  path('available/', cook_views.available, name='available'),
  path('acceptorder/<str:order_id>', cook_views.accept_order, name='accept_order'),
  path('rejectorder/<str:order_id>', cook_views.reject_order, name='reject_order'),
  path('cookingtodelivery/<str:order_id>', cook_views.cooking_to_delivery, name='cooking_to_delivery'),
  path('completeddelivery/<str:order_id>', cook_views.completed_delivery, name='completed_delivery'),
  path('dish/<str:dish_id>/reviews', cook_views.reviews_for_dish, name='reviews_for_dish'),
  path('dish_review/<str:dish_review_id>/report/<str:reason>', cook_views.report_dish_review, name='report_dish_review'),
  path('disabledish/<str:dish_id>', cook_views.cook_disable_dish, name='cook_disable_dish'),
  path('enabledish/<str:dish_id>', cook_views.cook_enable_dish, name='cook_enable_dish'),
  path('editdish/<str:dish_id>', cook_views.cook_edit_dish, name='cook_edit_dish'),
  path('myaccount/',cook_views.myaccount, name='myaccount'),
  path('orderhistory/', cook_views.order_history, name='order_history')
]
