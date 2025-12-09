from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tareas.urls')),  # Incluye las URLs de la app tareas

    path('accounts/login/', auth_views.LoginView.as_view(template_name='registro/login.html'), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),  # URLs de autenticación
# URLs para autenticación (si necesitas personalizar)
    path('login/', auth_views.LoginView.as_view(template_name='registro/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

# Solo en desarrollo: servir archivos media
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)