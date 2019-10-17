#from urls.cook_urls import urlpatterns as cook_urls
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('customer/', include('homeeats_app.urls.customer_urls')),
]

#urlpatterns+=cook_urls
