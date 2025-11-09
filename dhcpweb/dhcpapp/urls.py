from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('leases/', views.leases_list, name='leases_list'),
]

