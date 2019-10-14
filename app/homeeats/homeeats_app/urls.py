#from urls.cook_urls import urlpatterns as cook_urls
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

#urlpatterns+=cook_urls
