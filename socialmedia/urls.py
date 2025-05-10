"""
URL configuration for socialmedia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from api.views import (
    home_view, profile_view, edit_profile_view, feed_view, 
    logout_view, register_view, login_view, connections_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('profile/edit/', edit_profile_view, name='edit_profile'),
    path('profile/', profile_view, name='profile_view'),
    path('profile/<str:username>/', profile_view, name='profile_view'),
    path('feed/', feed_view, name='feed'),
    path('logout/', logout_view, name='logout'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('connections/', connections_view, name='connections_view'),
    
    # Include the API URLs
    path('api/', include('api.urls')),
    # Include Knox URLs
    path('api/auth/', include('knox.urls')),
]
