from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse


def google_verification(request):
    return HttpResponse(
        "google-site-verification: google000866ca78b2b004.html",
        content_type="text/html"
    )


def sitemap(request):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://www.fsrtech.com.br/</loc>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
</urlset>
"""

    return HttpResponse(xml, content_type="application/xml")


urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'google000866ca78b2b004.html',
        google_verification,
        name='google_verification'
    ),

    path(
        'sitemap.xml',
        sitemap,
        name='sitemap'
    ),

    path('', include('pedidos.urls')),
]