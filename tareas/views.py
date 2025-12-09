from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from .models import Tarea
from django.contrib import messages
from .forms import RegistroUsuarioForm, PersonalForm, PersonalSearchForm  # <-- AÑADIR LOS NUEVOS FORMS
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from .models import Personal, Tarea
from django.db.models import Q
from .forms import DependenciaForm

def home(request):
    """
    Página de inicio - redirige al dashboard si ya está autenticado
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tareas/home.html')

@login_required
def dashboard(request):
    """
    Dashboard principal - requiere autenticación
    """
    try:
        # Obtener datos para el dashboard
        total_tareas = Tarea.objects.count()
        tareas_pendientes = Tarea.objects.filter(estado_tarea='pendiente').count()
        tareas_en_progreso = Tarea.objects.filter(estado_tarea='en_progreso').count()
        tareas_completadas = Tarea.objects.filter(estado_tarea='completada').count()
        
        # Tareas del usuario actual
        mis_tareas = Tarea.objects.filter(
            mostrar=True, 
            estado_tarea__in=['pendiente', 'en_progreso']
        )
        
        # Estadísticas por categoría
        tareas_por_categoria = Tarea.objects.values('categoria').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Tareas urgentes
        tareas_urgentes = Tarea.objects.filter(
            modalidad='urgente',
            estado_tarea__in=['pendiente', 'en_progreso']
        )[:5]
        
        # Tareas próximas a vencer (en los próximos 7 días)
        fecha_limite = timezone.now().date() + timedelta(days=7)
        tareas_proximas_vencer = Tarea.objects.filter(
            fecha_fin_prevista__lte=fecha_limite,
            fecha_fin_prevista__gte=timezone.now().date(),
            estado_tarea__in=['pendiente', 'en_progreso']
        )[:5]
        
        # Datos para gráficos
        estados_tareas = ['Pendientes', 'En Progreso', 'Completadas']
        counts_estados = [tareas_pendientes, tareas_en_progreso, tareas_completadas]
        
        categorias = [item['categoria'] for item in tareas_por_categoria]
        counts_categorias = [item['total'] for item in tareas_por_categoria]
        
        context = {
            'total_tareas': total_tareas,
            'tareas_pendientes': tareas_pendientes,
            'tareas_en_progreso': tareas_en_progreso,
            'tareas_completadas': tareas_completadas,
            'mis_tareas': mis_tareas,
            'tareas_urgentes': tareas_urgentes,
            'tareas_proximas_vencer': tareas_proximas_vencer,
            'estados_tareas': estados_tareas,
            'counts_estados': counts_estados,
            'categorias': categorias,
            'counts_categorias': counts_categorias,
        }
        
        return render(request, 'tareas/dashboard.html', context)
        
    except Exception as e:
        # En caso de error, mostrar página básica
        context = {
            'error': str(e)
        }
        return render(request, 'tareas/dashboard.html', context)

@login_required
def lista_usuarios_simple(request):
    """
    Vista simple para mostrar usuarios con botones
    Tabla con usuarios del sistema y botones de acción (sin funcionalidad)
    """
    usuarios = User.objects.all().order_by('username')
    
    context = {
        'usuarios': usuarios,
        'total_usuarios': usuarios.count(),
    }
    
    return render(request, 'tareas/lista_usuarios_simple.html', context)

def registro_usuario(request):
    """
    Vista para registrar nuevos usuarios
    """
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Usuario registrado exitosamente! Ahora puede iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroUsuarioForm()
    
    context = {
        'form': form,
        'titulo': 'Registro de Nuevo Usuario'
    }
    return render(request, 'registro/registro_usuario.html', context)


# ========== VISTAS BASADAS EN CLASES PARA PERSONAL ==========

class PersonalListView(LoginRequiredMixin, ListView):
    """
    Vista para listar todo el personal
    """
    model = Personal
    template_name = 'tareas/personal_lista.html'
    context_object_name = 'personal_list'  # CAMBIAR DE 'page_obj' A 'personal_list'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Obtener parámetros de búsqueda
        query = self.request.GET.get('query', '')
        dependencia_id = self.request.GET.get('dependencia', '')
        
        # Aplicar filtros
        if query:
            queryset = queryset.filter(
                Q(cedula__icontains=query) |
                Q(nombre__icontains=query) |
                Q(apellido__icontains=query) |
                Q(usuario__username__icontains=query)
            )
        
        if dependencia_id:
            queryset = queryset.filter(dependencia_id=dependencia_id)
        
        return queryset.order_by('apellido', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agregar formulario de búsqueda
        context['search_form'] = PersonalSearchForm(self.request.GET or None)
        context['total_personal'] = Personal.objects.count()
        
        # Para paginación
        context['is_paginated'] = True
        context['page_obj'] = context.get('page_obj')
        
        return context

class PersonalDetailView(LoginRequiredMixin, DetailView):
    """
    Vista para ver detalles de un personal
    """
    model = Personal
    template_name = 'tareas/personal_detail.html'
    context_object_name = 'personal'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personal = self.get_object()
        
        # Agregar información de tareas relacionadas
        context['tareas_asignadas'] = Tarea.objects.filter(personal_asignado=personal)
        context['tareas_supervisadas'] = Tarea.objects.filter(supervisor=personal)
        context['tareas_como_participante'] = Tarea.objects.filter(participantes=personal)
        
        return context


class PersonalCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Vista para crear nuevo personal
    """
    model = Personal
    form_class = PersonalForm
    template_name = 'tareas/personal_form.html'
    success_url = reverse_lazy('personal_lista')
    permission_required = 'tareas.add_personal'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Agregar Nuevo Personal'
        context['submit_text'] = 'Guardar Personal'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Personal creado exitosamente.')
        return super().form_valid(form)


class PersonalUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Vista para editar personal existente
    """
    model = Personal
    form_class = PersonalForm
    template_name = 'tareas/personal_form.html'
    success_url = reverse_lazy('personal_lista')
    permission_required = 'tareas.change_personal'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Personal: {self.object.nombre_completo}'
        context['submit_text'] = 'Actualizar Personal'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Personal actualizado exitosamente.')
        return super().form_valid(form)


class PersonalDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Vista para eliminar personal
    """
    model = Personal
    template_name = 'tareas/personal_confirm_delete.html'
    success_url = reverse_lazy('personal_lista')
    permission_required = 'tareas.delete_personal'
    context_object_name = 'personal'
    
    def delete(self, request, *args, **kwargs):
        personal = self.get_object()
        # Guardar información para el mensaje
        nombre = personal.nombre_completo
        # Eliminar también el usuario asociado
        if personal.usuario:
            personal.usuario.delete()
        
        messages.success(request, f'Personal "{nombre}" eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


@login_required
def crear_dependencia(request):
    if request.method == 'POST':
        form = DependenciaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dependencia creada exitosamente.')
            return redirect('personal_nuevo')  # Regresa al formulario de Personal
    else:
        form = DependenciaForm()
    
    return render(request, 'tareas/dependencia_form.html', {'form': form})