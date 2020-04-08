from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user/<slug:username>', views.get_user),
]
