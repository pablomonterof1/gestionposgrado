from django import forms
from .models import Admision, DisenoCurricular, Titulacion

class AdmisionForm(forms.ModelForm):
    class Meta:
        model = Admision
        fields = ['tipodedato', 'descripcion', 'valor']

        widgets = {
      
            'tipodedato': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Tipo de dato'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor'}),


        }
        labels = {
    
            'tipodedato': 'Tipo de dato',
            'descripcion': 'Descripción',
            'valor': 'Valor',
         
        }


class DisenoCurricularForm(forms.ModelForm):
    class Meta:
        model = DisenoCurricular
        fields = ['nombre', 'tipodedato', 'descripcion', 'valor']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'tipodedato': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Tipo de dato'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor'}),


        }
        labels = {
            'nombre': 'Nombre',
            'tipodedato': 'Tipo de dato',
            'descripcion': 'Descripción',
            'valor': 'Valor',
        }


class TitulacionForm(forms.ModelForm):
    class Meta:
        model = Titulacion
        fields = ['nombre', 'tipodedato', 'descripcion', 'valor']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'tipodedato': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Tipo de dato'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor'}),


        }
        labels = {
            'nombre': 'Nombre',
            'tipodedato': 'Tipo de dato',
            'descripcion': 'Descripción',
            'valor': 'Valor',
        }

