from django.contrib import admin
from .models import *

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']

@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado', 'cod_mun']
    list_filter = ['estado']
    search_fields = ['nombre', 'cod_mun']

@admin.register(Parroquia)
class ParroquiaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'municipio', 'cod_parroquia', 'cod_mun']
    list_filter = ['municipio', 'municipio__estado']
    search_fields = ['nombre', 'cod_parroquia']

@admin.register(Institucion)
class InstitucionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'email', 'fecha_creacion']
    
    def has_add_permission(self, request):
        # Solo permitir agregar una institución si no existe ninguna
        if Institucion.objects.exists() and not request.user.is_superuser:
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Solo el superusuario puede eliminar la institución
        return request.user.is_superuser

@admin.register(Dependencia)
class DependenciaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'coordinador', 'fecha_creacion']
    list_filter = ['tipo']
    search_fields = ['nombre']

@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'nombre_completo', 'dependencia', 'fecha_ingreso']
    list_filter = ['dependencia', 'fecha_ingreso']
    search_fields = ['cedula', 'nombre', 'apellido']
    date_hierarchy = 'fecha_ingreso'

class BitacoraInline(admin.TabularInline):
    model = Bitacora
    extra = 0
    readonly_fields = ['personal', 'accion', 'descripcion', 'fecha_accion']
    can_delete = False

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'modalidad', 'estado_tarea', 
                   'porcentaje_avance', 'fecha_inicio', 'fecha_fin_prevista', 'supervisor']
    list_filter = ['categoria', 'modalidad', 'estado_tarea', 'municipio', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ['fecha_creacion']
    inlines = [BitacoraInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'categoria', 'modalidad', 'estado_tarea')
        }),
        ('Ubicación', {
            'fields': ('municipio', 'parroquia')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin_prevista', 'fecha_fin_real', 'fecha_creacion')
        }),
        ('Personal', {
            'fields': ('participantes', 'supervisor', 'personal_asignado', 'personal_reasignado')
        }),
        ('Progreso y Medición', {
            'fields': ('unidad_medida', 'cantidad', 'porcentaje_avance')
        }),
        ('Observaciones', {
            'fields': ('mostrar', 'causa_no_culminacion', 'observaciones')
        }),
    )

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ['tarea', 'personal', 'accion', 'fecha_accion']
    list_filter = ['accion', 'fecha_accion']
    search_fields = ['tarea__titulo', 'personal__nombre', 'personal__apellido']
    readonly_fields = ['fecha_accion']
    date_hierarchy = 'fecha_accion'