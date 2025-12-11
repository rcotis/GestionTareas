from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Estado(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
    
    def __str__(self):
        return self.nombre

class Municipio(models.Model):
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    cod_mun = models.CharField(max_length=10, unique=True)
    
    class Meta:
        verbose_name = "Municipio"
        verbose_name_plural = "Municipios"
    
    def __str__(self):
        return f"{self.nombre} - {self.estado.nombre}"

class Parroquia(models.Model):
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    cod_parroquia = models.CharField(max_length=10)
    cod_mun = models.CharField(max_length=10)
    
    class Meta:
        verbose_name = "Parroquia"
        verbose_name_plural = "Parroquias"
        unique_together = ['municipio', 'cod_parroquia']
    
    def __str__(self):
        return f"{self.nombre} - {self.municipio.nombre}"

class Institucion(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to='institucion/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Institución"
        verbose_name_plural = "Instituciones"
    
    def __str__(self):
        return self.nombre

class Dependencia(models.Model):
    TIPO_DEPENDENCIA = [
        ('coordinacion', 'Coordinación'),
        ('unidad', 'Unidad'),
        ('seccion', 'Sección'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_DEPENDENCIA)
    coordinador = models.ForeignKey('Personal', on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='coordinaciones')
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Dependencia"
        verbose_name_plural = "Dependencias"
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nombre}"

class Personal(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personal')
    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nac = models.DateField()
    fecha_ingreso = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    dependencia = models.ForeignKey(Dependencia, on_delete=models.SET_NULL, 
                                  null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    
    usuario_creado = models.BooleanField(default=False)
    password_temporal = models.CharField(max_length=100, blank=True, null=True)
    fecha_primer_acceso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Personal"
        verbose_name_plural = "Personal"
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.cedula} - {self.nombre} {self.apellido}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

class Tarea(models.Model):
    CATEGORIA_CHOICES = [
        ('administrativa', 'Administrativa'),
        ('operativa', 'Operativa'),
        ('tecnica', 'Técnica'),
        ('logistica', 'Logística'),
        ('otra', 'Otra'),
    ]
    
    MODALIDAD_CHOICES = [
        ('normal', 'Normal'),
        ('urgente', 'Urgente'),
        ('prioritaria', 'Prioritaria'),
    ]
    
    ESTADO_TAREA_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('rechazada', 'Rechazada'),
    ]
    
    # Información básica
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    modalidad = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='normal')
    estado_tarea = models.CharField(max_length=20, choices=ESTADO_TAREA_CHOICES, default='pendiente')
    
    # Ubicación
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE)
    parroquia = models.ForeignKey(Parroquia, on_delete=models.CASCADE)
    
    # Fechas
    fecha_inicio = models.DateField()
    fecha_fin_prevista = models.DateField()
    fecha_fin_real = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Personal involucrado
    participantes = models.ManyToManyField(Personal, related_name='tareas_participantes')
    supervisor = models.ForeignKey(Personal, on_delete=models.CASCADE, 
                                 related_name='tareas_supervisadas')
    personal_asignado = models.ForeignKey(Personal, on_delete=models.CASCADE, 
                                        related_name='tareas_asignadas')
    personal_reasignado = models.ForeignKey(Personal, on_delete=models.SET_NULL, 
                                          null=True, blank=True, 
                                          related_name='tareas_reasignadas')
    
    # Medición y progreso
    unidad_medida = models.CharField(max_length=50)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_avance = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Control y observaciones
    mostrar = models.BooleanField(default=True)
    causa_no_culminacion = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_tarea_display()}"
    
    @property
    def esta_vencida(self):
        from django.utils import timezone
        return self.fecha_fin_prevista < timezone.now().date() and self.porcentaje_avance < 100
    
    @property
    def puede_ser_completada(self):
        return self.porcentaje_avance == 100 and self.estado_tarea != 'completada'
    
    def get_porcentaje_display(self):
        """Retorna la clase CSS según el porcentaje de avance"""
        if self.porcentaje_avance == 100:
            return 'success'
        elif self.porcentaje_avance >= 75:
            return 'info'
        elif self.porcentaje_avance >= 50:
            return 'warning'
        else:
            return 'danger'

class Bitacora(models.Model):
    TIPO_ACCION_CHOICES = [
        ('creacion', 'Creación'),
        ('actualizacion', 'Actualización'),
        ('completado', 'Completado'),
        ('rechazo', 'Rechazo'),
        ('reasignacion', 'Reasignación'),
    ]
    
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='bitacoras')
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
    accion = models.CharField(max_length=20, choices=TIPO_ACCION_CHOICES)
    descripcion = models.TextField()
    fecha_accion = models.DateTimeField(auto_now_add=True)
    datos_anteriores = models.JSONField(blank=True, null=True)
    datos_nuevos = models.JSONField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Bitácora"
        verbose_name_plural = "Bitácoras"
        ordering = ['-fecha_accion']
    
    def __str__(self):
        return f"{self.tarea.titulo} - {self.get_accion_display()} - {self.fecha_accion}"