from django.urls import path

from . import views


urlpatterns = [
    path('stock/', views.stock_list, name='stock_list'),
]