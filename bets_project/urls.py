"""
URL Configuration for bets_project

This matches the PHP structure:
- / : Public area (login, register)
- /inside/ : User area (betting, account management)
- /adm/ : Custom admin area (NOT Django admin)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    # Django admin (keep for utilities, but hide from users)
    path('django-admin/', admin.site.urls),

    # Public area (root)
    path('', core_views.home, name='home'),
    path('login/', core_views.login_view, name='login'),
    path('logout/', core_views.logout_view, name='logout'),
    path('register/', core_views.register_view, name='register'),
    path('recover/', core_views.password_recovery, name='password_recovery'),

    # User area (authenticated users)
    path('inside/', include('user_area.urls')),

    # Custom admin area (permission-based, NOT Django admin)
    path('adm/', include('admin_panel.urls')),

    # API endpoints (optional, for future AJAX calls)
    # path('api/', include('core.api_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
