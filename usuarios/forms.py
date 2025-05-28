from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import DocumentosUsuario
from django.forms.widgets import ClearableFileInput

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, label='Nombre')
    last_name = forms.CharField(required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name",
                  "email", "password1", "password2")



class DocumentoUsuarioForm(forms.ModelForm):
    class Meta:
        model = DocumentosUsuario
        fields = ['titulo3', 'solicitudinscripcion', 'experiencialaboral', 'comprobantepago']
        labels = {
            'titulo3': 'Título de Tercer Nivel',
            'solicitudinscripcion': 'Solicitud de Inscripción',
            'experiencialaboral': 'Experiencia Laboral',
            'comprobantepago': 'Comprobante de Pago',
        }
        widgets = {
            'titulo3': ClearableFileInput(attrs={'class': 'form-control'}),
            'solicitudinscripcion': ClearableFileInput(attrs={'class': 'form-control'}),
            'experiencialaboral': ClearableFileInput(attrs={'class': 'form-control'}),
            'comprobantepago': ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, ClearableFileInput):
                # usamos solo el input, sin texts extra
                field.widget.template_name = 'widgets/only_file_input.html'