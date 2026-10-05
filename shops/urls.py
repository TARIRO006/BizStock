from django.urls import path

from . import views


urlpatterns = [
    path('stock/', views.stock_list, name='stock_list'),
    path('locations/', views.location_list, name='location_list'),
    path('locations/add/', views.location_create, name='location_create'),
    path('locations/<int:location_id>/edit/', views.location_edit, name='location_edit'),
    path('stock/add/', views.stock_create, name='stock_create'),
    path('movements/', views.movement_list, name='movement_list'),
    path('stock/transfer/', views.stock_transfer, name='stock_transfer'),
]