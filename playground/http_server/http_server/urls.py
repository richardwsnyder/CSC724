"""http_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import include, path

import user_profile.views as views

urlpatterns = [
    path('', views.index, name='index'),
    path('posts', views.get_posts),
    path('posts/<slug:username>', views.get_posts_remote),
    path('directory', views.get_profile_directory),
    path('user/<slug:username>', views.get_user),
    path('admin/', admin.site.urls),
]
