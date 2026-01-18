from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # User management (Admin)
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/edit/<int:user_id>/', views.user_edit, name='user_edit'),

    # Sidebar pages
    path('share-register/', views.share_register, name='share_register'),
    path('shareholders/', views.shareholders_page, name='shareholders'),
    path('directors/', views.directors_page, name='directors'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('settings/', views.settings_page, name='settings'),
    path('help/', views.help_page, name='help'),
]
