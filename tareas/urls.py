# from django.urls import path
# from . import views
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    PersonalListView, PersonalDetailView, 
    PersonalCreateView, PersonalUpdateView, PersonalDeleteView
)
urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('usuarios/', views.lista_usuarios_simple, name='lista_usuarios_simple'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
    
    # Modulo de personal
    path('personal/', PersonalListView.as_view(), name='personal_lista'),
    path('personal/nuevo/', PersonalCreateView.as_view(), name='personal_nuevo'),  
    path('personal/<int:pk>/', PersonalDetailView.as_view(), name='personal_detalle'),  
    path('personal/<int:pk>/editar/', PersonalUpdateView.as_view(), name='personal_editar'),  
    path('personal/<int:pk>/eliminar/', PersonalDeleteView.as_view(), name='personal_eliminar'), 

    # Dependencias
    path('dependencia/nueva/', views.crear_dependencia, name='dependencia_nueva'),
]