from .models import Institucion

def institucion_context(request):
    try:
        institucion = Institucion.objects.first()
    except Institucion.DoesNotExist:
        institucion = None
    
    return {
        'institucion': institucion
    }