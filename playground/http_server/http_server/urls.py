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
    path('posts', views.get_posts, name='get-posts'),
    path('posts/<slug:username>', views.get_posts_remote, name='get-posts-remote'),
    path('directory', views.get_profile_directory, name='get-directory'),
    path('feed', views.get_feed, name='get-feed'),
    path('user/<slug:username>', views.get_user, name='get-user'),
    path('user/<slug:username>/follow', views.addToFollowing, name='add-to-following-list'),
    path('user/<slug:username>/unfollow', views.removeFromFollowing, name='remove-from-following-list'),
    path('api/posts', views.api_get_posts),
    path('api/posts/all', views.api_get_posts_all),
    path('api/feed', views.api_get_feed),
    path('api/profile', views.api_get_profile),
    path('api/user/<slug:username>', views.api_get_user),
    path('search_user', views.search_user),
    path('admin/', admin.site.urls),
]
