from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import DocumentosUsuarioPEM
from django.forms.widgets import ClearableFileInput
from usuarios.models import PerfilUsuario, PerfilAcademicoUsuario

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, label='Nombre')
    last_name = forms.CharField(required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name",
                  "email", "password1", "password2")


class UserSelfForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if email:
            qs = User.objects.exclude(pk=self.instance.pk).filter(email=email)
            if qs.exists():
                raise forms.ValidationError('El correo ya está registrado por otro usuario.')
        return email

class UserSelfFormDP(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if email:
            qs = User.objects.exclude(pk=self.instance.pk).filter(email=email)
            if qs.exists():
                raise forms.ValidationError('El correo ya está registrado por otro usuario.')
        return email

class PerfilUsuarioSelfForm(forms.ModelForm):
    # Fuerza formato correcto para <input type="date">
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'},
            format='%Y-%m-%d',      # <- MUY IMPORTANTE
        ),
        input_formats=['%Y-%m-%d'],  # <- Para parsear el POST del browser
    )

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)

        # Si vienes con instance (GET), asegúrate que el initial respete el formato
        if self.instance and self.instance.pk and self.instance.fecha_nacimiento:
            self.initial['fecha_nacimiento'] = self.instance.fecha_nacimiento.strftime('%Y-%m-%d')

    class Meta:
        model = PerfilUsuario
        fields = ['ci', 'telefono', 'fecha_nacimiento', 'nacionalidad', 'sexo', 'provincia']
        widgets = {
            'ci': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_ci(self):
        ci = (self.cleaned_data.get('ci') or '').strip() or None
        if ci:
            qs = PerfilUsuario.objects.exclude(pk=self.instance.pk).filter(ci=ci)
            if qs.exists():
                raise forms.ValidationError('La cédula/CI ya está registrada en otro usuario.')
        return ci

class PerfilAcademicoSelfForm(forms.ModelForm):
    class Meta:
        model = PerfilAcademicoUsuario
        fields = ['titulo_grado', 'titulo_postgrado_maestria', 'titulo_postgrado_doctorado']
        widgets = {
            'titulo_grado': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo_postgrado_maestria': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo_postgrado_doctorado': forms.TextInput(attrs={'class': 'form-control'}),
        }



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