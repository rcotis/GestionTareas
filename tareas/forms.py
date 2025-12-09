from django import forms
from django.contrib.auth.models import User
from .models import Personal, Dependencia
from django.contrib.auth.forms import UserCreationForm

class RegistroUsuarioForm(UserCreationForm):
    """
    Formulario para registrar nuevos usuarios en el sistema
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        }),
        label='Correo Electrónico',
        help_text='Ingresa un correo válido que uses frecuentemente.'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombres'
        }),
        label='Nombres'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos'
        }),
        label='Apellidos'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Nombre de Usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar todos los campos con clases de Bootstrap
        for field_name in self.fields:
            if field_name not in ['username', 'password1', 'password2']:  # Ya configurados arriba
                continue
            
            field = self.fields[field_name]
            
            if field_name == 'username':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Nombre de usuario para iniciar sesión',
                    'autocomplete': 'username'
                })
                field.help_text = 'Requerido. 150 caracteres o menos. Solo letras, números y @/./+/-/_'
            
            elif field_name == 'password1':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Elige una contraseña segura',
                    'autocomplete': 'new-password'
                })
            
            elif field_name == 'password2':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Repite la contraseña para verificar',
                    'autocomplete': 'new-password'
                })
                field.help_text = 'Ingresa la misma contraseña que arriba, para verificación.'
    
    def clean_email(self):
        """
        Validar que el email no esté ya registrado
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado en el sistema.')
        return email
    
    def clean_username(self):
        """
        Validar que el nombre de usuario no esté ya registrado
        """
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso. Por favor elige otro.')
        return username
    
    def save(self, commit=True):
        """
        Guardar el usuario con información adicional
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = True  # Activar automáticamente
        
        if commit:
            user.save()
        
        return user


class PersonalForm(forms.ModelForm):
    """
    Formulario para crear y editar Personal
    """
    # Campos adicionales para el usuario
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        label='Nombre de Usuario'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
        label='Correo Electrónico'
    )
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        label='Contraseña (dejar vacío para no cambiar)',
        help_text='Solo llena si deseas cambiar la contraseña'
    )
    
    # Campos para crear nueva dependencia (si no existe)
    crear_nueva_dependencia = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Crear nueva dependencia'
    )
    
    nueva_dependencia_nombre = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de nueva dependencia'}),
        label='Nombre de nueva dependencia'
    )
    
    nueva_dependencia_tipo = forms.ChoiceField(
        required=False,
        choices=Dependencia.TIPO_DEPENDENCIA,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de dependencia'
    )
    
    class Meta:
        model = Personal
        fields = ['cedula', 'nombre', 'apellido', 'fecha_nac', 
                  'fecha_ingreso', 'dependencia', 'telefono', 'direccion']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'V-12345678'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'fecha_nac': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_ingreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dependencia': forms.Select(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0412-1234567'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
        }
        labels = {
            'cedula': 'Cédula de Identidad',
            'fecha_nac': 'Fecha de Nacimiento',
            'fecha_ingreso': 'Fecha de Ingreso',
            'dependencia': 'Dependencia/Departamento',
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        # Si no hay dependencias, sugerir crear una nueva
        dependencias_existen = Dependencia.objects.exists()
        
        if not dependencias_existen:
            self.fields['dependencia'].required = False
            self.fields['crear_nueva_dependencia'].initial = True
            self.fields['crear_nueva_dependencia'].widget.attrs['disabled'] = True
            self.fields['nueva_dependencia_nombre'].required = True
            self.fields['nueva_dependencia_tipo'].required = True
        
        # Si es una instancia existente, cargar datos del usuario
        if instance and instance.usuario:
            self.fields['username'].initial = instance.usuario.username
            self.fields['email'].initial = instance.usuario.email
            self.fields['password'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        crear_nueva = cleaned_data.get('crear_nueva_dependencia')
        
        # Validar opción de dependencia
        if crear_nueva:
            # Validar campos de nueva dependencia
            if not cleaned_data.get('nueva_dependencia_nombre'):
                self.add_error('nueva_dependencia_nombre', 'Este campo es requerido cuando se crea nueva dependencia')
            if not cleaned_data.get('nueva_dependencia_tipo'):
                self.add_error('nueva_dependencia_tipo', 'Este campo es requerido cuando se crea nueva dependencia')
        else:
            # Validar que se seleccione una dependencia existente
            if not cleaned_data.get('dependencia'):
                self.add_error('dependencia', 'Debe seleccionar una dependencia existente o crear una nueva')
        
        # Si no hay dependencias en el sistema, forzar creación
        if not Dependencia.objects.exists():
            cleaned_data['crear_nueva_dependencia'] = True
        
        return cleaned_data
    
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        instance = self.instance
        
        # Verificar que la cédula no esté duplicada
        qs = Personal.objects.filter(cedula=cedula)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        
        if qs.exists():
            raise forms.ValidationError('Esta cédula ya está registrada en el sistema.')
        return cedula
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        instance = self.instance
        
        # Verificar que el username no esté duplicado
        qs = User.objects.filter(username=username)
        if instance and instance.usuario:
            qs = qs.exclude(pk=instance.usuario.pk)
        
        if qs.exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        instance = self.instance
        
        # Verificar que el email no esté duplicado
        qs = User.objects.filter(email=email)
        if instance and instance.usuario:
            qs = qs.exclude(pk=instance.usuario.pk)
        
        if qs.exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email
    
    def save(self, commit=True):
        # Obtener o crear el usuario
        instance = super().save(commit=False)
        
        # Manejar creación de nueva dependencia
        crear_nueva = self.cleaned_data.get('crear_nueva_dependencia', False)
        
        if crear_nueva:
            # Crear nueva dependencia
            nueva_dependencia = Dependencia.objects.create(
                nombre=self.cleaned_data['nueva_dependencia_nombre'],
                tipo=self.cleaned_data['nueva_dependencia_tipo'],
                descripcion=f'Creada automáticamente para {self.cleaned_data.get("nombre", "")} {self.cleaned_data.get("apellido", "")}'
            )
            instance.dependencia = nueva_dependencia
        
        # Manejar creación/actualización de usuario
        if not instance.usuario:
            # Crear nuevo usuario
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data.get('password') or 'temp_password_123',
                first_name=self.cleaned_data.get('nombre', ''),
                last_name=self.cleaned_data.get('apellido', '')
            )
            instance.usuario = user
        else:
            # Actualizar usuario existente
            instance.usuario.username = self.cleaned_data['username']
            instance.usuario.email = self.cleaned_data['email']
            instance.usuario.first_name = self.cleaned_data.get('nombre', instance.usuario.first_name)
            instance.usuario.last_name = self.cleaned_data.get('apellido', instance.usuario.last_name)
            if self.cleaned_data.get('password'):
                instance.usuario.set_password(self.cleaned_data['password'])
            instance.usuario.save()
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance


class PersonalSearchForm(forms.Form):
    """
    Formulario para buscar personal
    """
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, apellido o cédula...'
        }),
        label=''
    )
    
    dependencia = forms.ModelChoiceField(
        queryset=Dependencia.objects.all(),
        required=False,
        empty_label="Todas las dependencias",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Filtrar por dependencia'
    )


class DependenciaForm(forms.ModelForm):
    class Meta:
        model = Dependencia
        fields = ['nombre', 'tipo', 'coordinador', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la dependencia'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'coordinador': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer coordinador opcional en el formulario
        self.fields['coordinador'].required = False
        self.fields['coordinador'].queryset = Personal.objects.all()