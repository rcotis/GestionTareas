from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    """
    Página de inicio
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'tareas/home.html')

@login_required
def dashboard(request):
    """
    Dashboard principal
    """
    return render(request, 'tareas/dashboard.html')

def registro_con_cedula(request):
    """
    Vista para registro con cédula (la haremos después)
    """
    # Por ahora solo renderiza un template básico
    return render(request, 'registro/registro_con_cedula.html', {
        'titulo': 'Completar Registro'
    })