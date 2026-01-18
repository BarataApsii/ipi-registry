from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('share-register/', views.share_register, name='share_register'),
    path('shareholders/', views.shareholders_page, name='shareholders'),
    path('transactions/', views.transaction_history, name='transactions'),
    path('directors/', views.directors_page, name='directors'),
    path('settings/', views.settings_page, name='settings'),
    path('help/', views.help_page, name='help'),
]
