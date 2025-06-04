from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import DocumentosUsuarioPEM
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
        model = DocumentosUsuarioPEM
        fields = ['docidentificacion', 'titulosenescyt', ]
        labels = {
            'docidentificacion': 'Copia de cédula de ciudadanía y certificado de votación vigentes',
            'titulosenescyt': 'Certificado de registro del título de tercer nivel expedido por la Secretaría de Educación Superior, Ciencia, Tecnología e Innovación (SENESCYT)',
        }
        widgets = {
            'docidentificacion': ClearableFileInput(attrs={'class': 'form-control'}),
            'titulosenescyt': ClearableFileInput(attrs={'class': 'form-control'}),
           
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, ClearableFileInput):
                # usamos solo el input, sin texts extra
                field.widget.template_name = 'widgets/only_file_input.html'
    
    def clean(self):
        cleaned_data = super().clean()

        docidentificacion = cleaned_data.get('docidentificacion')
        titulosenescyt = cleaned_data.get('titulosenescyt')

        instance = self.instance  # Documento existente

        if not docidentificacion and not instance.docidentificacion:
            self.add_error('docidentificacion', 'Este documento es obligatorio.')

        if not titulosenescyt and not instance.titulosenescyt:
            self.add_error('titulosenescyt', 'Este documento es obligatorio.')