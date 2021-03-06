from ..views import customer_views
from django.urls import path

urlpatterns = [
  path('dish/<int:dish_id>/', customer_views.dish, name='customer_dish'), #url for dish detailed page
  path('home/', customer_views.home, name='customer_home'), #customer landing page
  path('editprofile/', customer_views.customer_edit_profile, name='customer_edit_profile'),
  path('cart/', customer_views.cart, name='cart'), #customer shopping cart
  path('addtocart/', customer_views.addtocart, name='addtocart'), #controller for adding dish to cart
  path('removefromcart/', customer_views.removefromcart, name='removefromcart'), #controller for removing dish from cart
  # path('removeItem/', customer_views.removeItem, name='removeItem'), #controller for adding dish to cart
  path('payment/', customer_views.payment, name='payment'), #controller for adding dish to cart
  path('checkout/', customer_views.checkout, name='checkout'), #customer checkout page
  path('orders/', customer_views.orders, name='orders'), #all current and past orders
  path('order/<int:order_id>/', customer_views.order, name='order'), #page for individual order
  path('cancelorder/', customer_views.cancel_order, name="cancel_order"),
  path('favorites/', customer_views.favorites, name='favorites'),
  path('togglefav/', customer_views.toggle_favorite, name='togglefav'),
  path('message/', customer_views.message, name='message'),
  path('myaccount/',customer_views.myaccount, name = 'myaccount'), #customer profile page
  path('change_current_address/<str:address_id>', customer_views.change_current_address, name='change_current_address'),
  path('delete_address/<str:address_id>', customer_views.delete_address, name='delete_address')
]
