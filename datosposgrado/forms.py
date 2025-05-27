from django import forms
from .models import ContratosDocentes

class ContratosDocentesForm(forms.ModelForm):
    class Meta:
        model = ContratosDocentes
        fields = ['docente', 'programadeposgrado', 'modulo', 'horasacademicas', 'valorxhora', 'certificacionpresupuestaria', 'fechacertificacionpresupuestaria', 'plazo', 'numerocontrato', 'numeromemorandotthh' ,'tipopersonalacademico', 'adenda', 'obsevaciones']

        widgets = {
            'docente': forms.Select(attrs={'class': 'form-control'}),
            'programadeposgrado': forms.Select(attrs={'class': 'form-control'}),
            'modulo': forms.Select(attrs={'class': 'form-control'}),
            'horasacademicas': forms.NumberInput(attrs={'class': 'form-control'}),
            'valorxhora': forms.NumberInput(attrs={'class': 'form-control'}),
            'certificacionpresupuestaria': forms.TextInput(attrs={'class': 'form-control'}),
            'fechacertificacionpresupuestaria': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'plazo': forms.TextInput(attrs={'class': 'form-control'}),
            'numerocontrato': forms.TextInput(attrs={'class': 'form-control'}),
            'numeromemorandotthh': forms.TextInput(attrs={'class': 'form-control'}),
            'tipopersonalacademico': forms.Select(attrs={'class': 'form-control'}, choices=[
                (1, 'Servicios profesionales'),
            ]),
            'adenda': forms.TextInput(attrs={'class': 'form-control'}),
            'obsevaciones': forms.Textarea(attrs={'class': 'form-control'}),
        }   
        labels = {
            'docente': 'Docente',
            'programadeposgrado': 'Programa de Posgrado',
            'modulo': 'Módulo',
            'horasacademicas': 'Horas Académicas',
            'valorxhora': 'Valor por Hora',
            'certificacionpresupuestaria': 'Certificación Presupuestaria',
            'fechacertificacionpresupuestaria': 'Fecha de Certificación Presupuestaria',
            'plazo': 'Plazo',
            'numerocontrato': 'Número de Contrato',
            'numeromemorandotthh': 'Número de Memorando TTHH',
            'tipopersonalacademico': 'Tipo de Personal Académico',
            'adenda': 'Adenda',
            'obsevaciones': 'Observaciones',
        }