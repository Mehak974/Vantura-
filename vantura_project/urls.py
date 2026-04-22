"""
Vantura URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Customize admin site
admin.site.site_header = 'Vantura Admin Panel'
admin.site.site_title = 'Vantura'
admin.site.index_title = 'Store Management'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('accounts/', include('accounts.urls')),
    path('robots.txt', lambda r: HttpResponse("User-agent: *\nAllow: /", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'store.views.error_404'
handler500 = 'store.views.error_500'
