from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

# Custom admin site settings
admin.site.site_header = 'IPI Group Share Registry'
admin.site.site_title = 'IPI Group Admin'
admin.site.index_title = 'Share Registry Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),  # Dashboard
    path('shareholders/', include('shareholders.urls')),  # Shareholders app
    path('accounts/', include('django.contrib.auth.urls')),  # Login/Logout

    # Redirect root URL to login page
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
]
