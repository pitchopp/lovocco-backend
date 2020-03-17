"""lovocco URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from backend import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api/admin', admin.site.urls),
    path('api/genders', views.genders),
    path('api/citys', views.cities),
    path('api/lovers/me', views.my_profile),
    path('api/lovers/candidates', views.candidates),
    path('api/lovers/<int:lover_id>/like', views.like),
    # Authentication
    path('api/authenticate', obtain_auth_token),
    path('api/register', views.register_user)
]