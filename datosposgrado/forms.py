from django import forms
from .models import ContratosDocentes, ContratoTutor , ContratoCoordinador

class ContratosDocentesForm(forms.ModelForm):
    class Meta:
        model = ContratosDocentes
        fields = ['docente', 'programadeposgrado', 'modulo', 'horasacademicas', 'valorxhora', 'certificacionpresupuestaria', 'fechacertificacionpresupuestaria', 'plazo', 'numerocontrato', 'numeromemorandotthh' ,'tipopersonalacademico', 'adenda', 'observaciones', 'urldocumento']

        widgets = {
            'docente': forms.Select(attrs={'class': 'form-control'}),
            'programadeposgrado': forms.Select(attrs={'class': 'form-control'}),
            'modulo': forms.Select(attrs={'class': 'form-control'}),
            'horasacademicas': forms.NumberInput(attrs={'class': 'form-control'}),
            'valorxhora': forms.NumberInput(attrs={'class': 'form-control'}),
            'certificacionpresupuestaria': forms.TextInput(attrs={'class': 'form-control'}),
            'fechacertificacionpresupuestaria': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'plazo': forms.TextInput(attrs={'class': 'form-control'}),
            'numerocontrato': forms.TextInput(attrs={'class': 'form-control'}),
            'numeromemorandotthh': forms.TextInput(attrs={'class': 'form-control'}),
            'tipopersonalacademico': forms.Select(attrs={'class': 'form-control'}, choices=[
                (1, 'Servicios profesionales'),
            ]),
            'adenda': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
            'urldocumento': forms.URLInput(attrs={'class': 'form-control'}),
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
            'observaciones': 'Observaciones',
            'urldocumento': 'URL del Documento',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fechacertificacionpresupuestaria'].input_formats = ['%Y-%m-%d']

class ContratoTutorForm(forms.ModelForm):
    class Meta:
        model = ContratoTutor
        fields = ['tutor', 'programadeposgrado', 'maestrante', 'plazo', 'certificacionpresupuestaria', 'fechacertificacionpresupuestaria', 'valorcontrato', 'numerocontrato', 'numeromemorandotthh', 'tipopersonalacademico', 'adenda', 'observaciones', 'urldocumento']

        widgets = {
            'tutor': forms.Select(attrs={'class': 'form-control'}),
            'programadeposgrado': forms.Select(attrs={'class': 'form-control'}),
            'maestrante': forms.Select(attrs={'class': 'form-control'}),
            'plazo': forms.TextInput(attrs={'class': 'form-control'}),
            'certificacionpresupuestaria': forms.TextInput(attrs={'class': 'form-control'}),
            'fechacertificacionpresupuestaria': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'valorcontrato': forms.NumberInput(attrs={'class': 'form-control'}),
            'numerocontrato': forms.TextInput(attrs={'class': 'form-control'}),
            'numeromemorandotthh': forms.TextInput(attrs={'class': 'form-control'}),
            'tipopersonalacademico': forms.Select(attrs={'class': 'form-control'}, choices=[
                (1, 'Servicios profesionales'),
            ]),
            'adenda': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
            'urldocumento': forms.URLInput(attrs={'class': 'form-control'}),
        }   
        labels = {
            'tutor': 'Tutor',
            'programadeposgrado': 'Programa de Posgrado',
            'maestrante': 'Maestrante',
            'plazo': 'Plazo',
            'certificacionpresupuestaria': 'Certificación Presupuestaria',
            'fechacertificacionpresupuestaria': 'Fecha de Certificación Presupuestaria',
            'valorcontrato': 'Valor del Contrato',
            'numerocontrato': 'Número de Contrato',
            'numeromemorandotthh': 'Número de Memorando TTHH',
            'tipopersonalacademico': 'Tipo de Personal Académico',
            'adenda': 'Adenda',
            'observaciones': 'Observaciones',
            'urldocumento': 'URL del Documento',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fechacertificacionpresupuestaria'].input_formats = ['%Y-%m-%d']

class ContratoCoordinadorForm(forms.ModelForm):
    class Meta:
        model = ContratoCoordinador
        fields = ['coordinador', 'programadeposgrado', 'certificacionpresupuestaria', 'fechacertificacionpresupuestaria', 'plazo', 'fechainicio', 'fechafin', 'honorario', 'numerocontrato', 'cargo','noactasseleccion','oficioentregadoporth','modalidadcontractuar','observaciones', 'urldocumento']

        widgets = {
            'coordinador': forms.Select(attrs={'class': 'form-control'}),
            'programadeposgrado': forms.Select(attrs={'class': 'form-control'}),
            'certificacionpresupuestaria': forms.TextInput(attrs={'class': 'form-control'}),
            'fechacertificacionpresupuestaria': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'plazo': forms.TextInput(attrs={'class': 'form-control'}),
            'fechainicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),   # nuevo
            'fechafin': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),     # nuevo
            'honorario': forms.NumberInput(attrs={'class': 'form-control'}),
            'numerocontrato': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'noactasseleccion': forms.TextInput(attrs={'class': 'form-control'}),
            'oficioentregadoporth': forms.TextInput(attrs={'class': 'form-control'}),
            'modalidadcontractuar': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
            'urldocumento': forms.URLInput(attrs={'class': 'form-control'}),
        }   
        labels = {
            'coordinador': 'Coordinador',
            'programadeposgrado': 'Programa de Posgrado',
            'certificacionpresupuestaria': 'Certificación Presupuestaria',
            'fechacertificacionpresupuestaria': 'Fecha de Certificación Presupuestaria',
            'plazo': 'Plazo',
            'fechainicio': 'Fecha de inicio',      # nuevo
            'fechafin': 'Fecha de fin',            # nuevo
            'honorario': 'Honorario',
            'numerocontrato': 'Número de Contrato',
            'cargo': 'Cargo',
            'noactasseleccion': 'Número de Acta de Selección',
            'oficioentregadoporth': 'Oficio Entregado por TTHH',
            'modalidadcontractuar': 'Modalidad Contractuar',
            'observaciones': 'Observaciones',
            'urldocumento': 'URL del Documento',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fechacertificacionpresupuestaria'].input_formats = ['%Y-%m-%d']
        self.fields['fechainicio'].input_formats = ['%Y-%m-%d']  # nuevo
        self.fields['fechafin'].input_formats = ['%Y-%m-%d']    # nuevo