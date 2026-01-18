from django.urls import path
from . import views

app_name = 'shareholders'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_shareholder, name='search_shareholder'),
    path('update_shares/<int:shareholder_id>/', views.update_shares, name='update_shares'),
    path('report/<int:shareholder_id>/', views.shareholder_report, name='shareholder_report'),
]
