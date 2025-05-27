from django import forms
from .models import ReactivosMultipleChoice
from django.contrib.auth import get_user_model
from tinymce.widgets import TinyMCE


User = get_user_model()

class ReactivosMultipleChoiceForm(forms.ModelForm):
    CORRECTA_CHOICES = [
        ('A', 'Opción A'),
        ('B', 'Opción B'),
        ('C', 'Opción C'),
        ('D', 'Opción D'),
    ]

    correcta = forms.ChoiceField(
        choices=CORRECTA_CHOICES,
        widget=forms.RadioSelect,
        label='Opción correcta'
    )

    class Meta:
        model = ReactivosMultipleChoice
        fields = ['enunciado', 'contribucion', 'opciona', 'opcionb', 'opcionc', 'opciond', 'correcta' , 'justificacion', 'bibliografia' , 'palabras_clave', 'tiempo_estimado']
        widgets = {
            'enunciado': TinyMCE(attrs={'cols': 80, 'rows': 10}),
            'contribucion': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Contribución'}),
            'opciona': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opción A'}),
            'opcionb': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opción B'}),
            'opcionc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opción C'}),
            'opciond': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opción D'}),
            'justificacion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Justificación'}),
            'bibliografia' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Bibliografía'}),
            'palabras_clave' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Palabras clave'}),
            'tiempo_estimado' : forms.NumberInput(attrs={'class': 'form-control',  }),
            # Add other fields as needed
        }
        labels = {
            'enunciado': 'Enunciado',
            'contribucion': 'Contribución',
            'opciona': 'Opción A',
            'opcionb': 'Opción B',
            'opcionc': 'Opción C',
            'opciond': 'Opción D',
            'justificacion': 'Justificación',
            'bibliografia' : 'Bibliografía',
            'palabras_clave' : 'Palabras clave',
            'tiempo_estimado' : 'Tiempo estimado',
            # Add other labels as needed
        }
    