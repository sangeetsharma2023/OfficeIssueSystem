from django.contrib import admin
from django.urls import path, include
from issues.views import user_login, user_logout
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('', include('issues.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
