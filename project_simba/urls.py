"""
URL configuration for project_simba project.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('jobcard/', include('jobcard.urls')),

    # Redirect root URL to jobcard/new/
    path('', lambda request: redirect('jobcard_create')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
