
from django.urls import path
from . import views

urlpatterns = [
    path('settings/', views.settings_home, name='settings_home'),
    path('settings/business/', views.business_settings, name='business_settings'),
]
