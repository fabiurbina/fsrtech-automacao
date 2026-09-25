"""
URL configuration for portal project.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def google_verification(request):
    return HttpResponse(
        "google-site-verification: google000866ca78b2b004.html",
        content_type="text/html"
    )


urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'google000866ca78b2b004.html',
        google_verification,
        name='google_verification'
    ),

    path('', include('pedidos.urls')),
]