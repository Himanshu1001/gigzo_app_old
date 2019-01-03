from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header  = 'Welcome to Gigzo Admin Dashboard' 
admin.site.site_title   = 'Gigzo Admin Dashboard'
admin.site.index_header = 'Admin'


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)