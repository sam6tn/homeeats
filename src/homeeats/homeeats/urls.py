"""homeeats URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from homeeats_app.views import admin_views

urlpatterns = [
    path('admin/cook/applications/', admin_views.cookApplications),
    # path('admin/cooks/', admin_views.cooks, name='admin_cooks'),
    path('admin/cooks/<int:cook_id>/', admin_views.cook, name='admin_cook'),
    # path('admin/customers/', admin_views.customers, name='admin_customers'),
    path('admin/customers/<int:customer_id>', admin_views.customer, name='admin_customer'),
    path('admin/reviews/reported/', admin_views.reportedreviews, name='admin_reportedreviews'),
    path('admin/', admin.site.urls),
    path('', include('homeeats_app.urls.main_urls')),
    path('cook/', include('homeeats_app.urls.cook_urls')),
    path('customer/', include('homeeats_app.urls.customer_urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
