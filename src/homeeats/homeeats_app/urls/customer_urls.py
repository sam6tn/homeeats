from ..views import customer_views
from django.urls import path

urlpatterns = [
  path('dish/<int:dish_id>/', customer_views.dish, name='customer_dish'), #url for dish detailed page
  path('home/', customer_views.home, name='customer_home'), #customer landing page
  path('editprofile/', customer_views.customer_edit_profile, name='customer_edit_profile'),
  path('cart/', customer_views.cart, name='cart'), #customer shopping cart
  path('addtocart/', customer_views.addtocart, name='addtocart'), #controller for adding dish to cart
  path('removeItem/', customer_views.removeItem, name='removeItem'), #controller for adding dish to cart
  path('payment/', customer_views.payment, name='payment'), #controller for adding dish to cart
  path('checkout/', customer_views.checkout, name='checkout'), #customer checkout page
  path('orders/', customer_views.orders, name='orders'), #all current and past orders
  path('order/<int:order_id>/', customer_views.order, name='order'), #page for individual order
  path('favorites/', customer_views.favorites, name='favorites'),
  path('togglefav/', customer_views.toggle_favorite, name='togglefav')
]
