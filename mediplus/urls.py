"""
URL configuration for mediplus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
"""
Main URL Configuration for mediplus project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Root view
def root_redirect(request):
    return HttpResponseRedirect('/swagger/')

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="MediPlus API Documentation",
        default_version='v1',
        description="API for MediPlus Healthcare Management System",
        terms_of_service="https://www.mediplus.com/terms/",
        contact=openapi.Contact(email="contact@mediplus.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root redirect to API documentation
    path('', root_redirect, name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints
    path('api/accounts/', include('mediplus.apps.accounts.urls')),
    path('api/patients/', include('mediplus.apps.patients.urls')),
    path('api/doctors/', include('mediplus.apps.doctors.urls')),
    path('api/appointments/', include('mediplus.apps.appointments.urls')),
    path('api/payments/', include('mediplus.apps.payments.urls')),
    path('api/pharmacies/', include('mediplus.apps.pharmacies.urls')),
    path('api/campaigns/', include('mediplus.apps.campaigns.urls')),
    path('api/admin/', include('mediplus.apps.admin_panel.urls')),
    path('api/notifications/', include('mediplus.apps.notifications.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
