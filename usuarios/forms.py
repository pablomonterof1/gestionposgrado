from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import DocumentosUsuario

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
        fields = [
            'titulo3', 'observaciontitulo3',
            'solicitudinscripcion', 'observacionsolicitudinscripcion',
            'experiencialaboral', 'observacionexperiencialaboral',
            'comprobantepago', 'observacioncomprobantepago'
        ]
        widgets = {
            'titulo3': forms.ClearableFileInput(),
            'solicitudinscripcion': forms.ClearableFileInput(),
            'experiencialaboral': forms.ClearableFileInput(),
            'comprobantepago': forms.ClearableFileInput(),
            'observaciontitulo3': forms.Textarea(attrs={'rows': 2}),
            'observacionsolicitudinscripcion': forms.Textarea(attrs={'rows': 2}),
            'observacionexperiencialaboral': forms.Textarea(attrs={'rows': 2}),
            'observacioncomprobantepago': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Validación opcional: asegúrate de que los archivos sean PDFs si quieres
        for field in ['titulo3', 'solicitudinscripcion', 'experiencialaboral', 'comprobantepago']:
            file = cleaned_data.get(field)
            if file and not file.name.endswith('.pdf'):
                self.add_error(field, 'El archivo debe ser un PDF.')
        return cleaned_data