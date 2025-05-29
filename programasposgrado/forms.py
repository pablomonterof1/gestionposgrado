from django import forms
from .models import Maestrias, Modulos, EspecialidadesMedicas, ModulosEM


#################################MAESTRIAS###########################################
class MaestriaForm(forms.ModelForm):
    class Meta:
        model = Maestrias
        fields = ['nombre', 'descripcion', 'evaluado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'evaluado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'evaluado': 'Evaluado',
        }

class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulos
        fields = [ 'nombre', 'codificacion']
        widgets = {

            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'codificacion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Codificación'}),
        }
        labels = {
            
            'nombre': 'Nombre',
            'codificacion': 'Codificación',
        }

#################################ESPECIALIDADESMEDICAS###########################################

class EspecialidadesMedicasForm(forms.ModelForm):
    class Meta:
        model = EspecialidadesMedicas
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
        }


class ModuloEMForm(forms.ModelForm):
    class Meta:
        model = ModulosEM
        fields = [ 'nombre', 'codificacion']
        widgets = {

            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'codificacion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Codificación'}),
        }
        labels = {
            
            'nombre': 'Nombre',
            'codificacion': 'Codificación',
        }


