from django import forms
from .models import ValorProgramaPosgrado, CoordinadorPrograma, CoordinadorPagos, ContratoDocenteGestion, ContratoTutorGestion, EstudianteProgramaGestion
from usuarios.models import User
from datosposgrado.models import ContratoCoordinador, ContratosDocentes
from django.contrib.contenttypes.models import ContentType
from programasposgrado.models import ProgramaPosgrado

class ValorProgramaPosgradoForm(forms.ModelForm):
    class Meta:
        model = ValorProgramaPosgrado
        fields = [
            'valorinscripcion', 'valormatricula',
            'plan_pago',
            'primeracolegiatura', 'segundacolegiatura',
            'valor_total', 'cuota_mensual',
            'moneda'
        ]
        widgets = {
            'valorinscripcion': forms.NumberInput(attrs={'class':'form-control', 'step':'0.01', 'min':'0'}),
            'valormatricula': forms.NumberInput(attrs={'class':'form-control', 'step':'0.01', 'min':'0'}),
            'plan_pago': forms.Select(attrs={'class':'form-select'}),
            'primeracolegiatura': forms.NumberInput(attrs={'class':'form-control', 'step':'0.01', 'min':'0'}),
            'segundacolegiatura': forms.NumberInput(attrs={'class':'form-control', 'step':'0.01', 'min':'0'}),
            'valor_total': forms.NumberInput(attrs={'class':'form-control', 'step':'0.01', 'min':'0'}),
            'cuota_mensual': forms.NumberInput(attrs={'class':'form-control', 'readonly':'readonly'}),
            'moneda': forms.TextInput(attrs={'class':'form-control', 'readonly':'readonly'}),
        }

    def clean(self):
        data = super().clean()
        # ya validamos no negativos en el modelo; aquí puedes añadir checks UX si quieres
        return data
    

class CoordinadorProgramaForm(forms.ModelForm):
    class Meta:
        model = CoordinadorPrograma
        fields = ['fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'fecha_inicio': 'Fecha de inicio',
            'fecha_fin': 'Fecha de fin',
        }


class ContratoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):

        return f"{obj.numerocontrato} — {obj.honorario} USD"



class CoordinadorPagosForm(forms.ModelForm):
    contrato = ContratoChoiceField(
        queryset=ContratoCoordinador.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Contrato'
    )

    class Meta:
        model = CoordinadorPagos
        fields = ['contrato', 'mes_pago', 'numero_factura', 'valor_total', 'numero_oficio_tramite', 'moneda']
        widgets = {
            'mes_pago': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'numero_oficio_tramite': forms.TextInput(attrs={'class': 'form-control'}),
            'moneda': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        programa = kwargs.pop('programa', None)
        coordinador_id = kwargs.pop('coordinador_id', None)
        contrato_fijo = kwargs.pop('contrato_fijo', None)

        super().__init__(*args, **kwargs)

        if contrato_fijo is not None:
            self.fields['contrato'].queryset = ContratoCoordinador.objects.filter(pk=contrato_fijo)

        elif programa and coordinador_id:
            ct = ContentType.objects.get_for_model(programa.__class__)

            self.fields['contrato'].queryset = ContratoCoordinador.objects.filter(
                programa_content_type=ct,
                programa_object_id=programa.id,
                coordinador=coordinador_id
            ).order_by('-created')

        else:
            self.fields['contrato'].queryset = ContratoCoordinador.objects.none()

        if not self.initial.get('moneda'):
            self.initial['moneda'] = 'USD'



class ContratoDocenteGestionForm(forms.ModelForm):
    class Meta:
        model = ContratoDocenteGestion
        fields = ['fecha_contratacion', 'pago_realizado', 'numero_factura', 'observaciones']
        widgets = {
            'fecha_contratacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'pago_realizado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'fecha_contratacion': 'Fecha de contratación',
            'pago_realizado': 'Pago realizado',
            'numero_factura': 'N° Factura',
            'observaciones': 'Observaciones (en caso de no estar pagado)',
        }



class ContratoTutorGestionForm(forms.ModelForm):
    class Meta:
        model = ContratoTutorGestion
        fields = ['fecha_contratacion', 'defendido', 'pago_realizado', 'numero_factura', 'observaciones']
        widgets = {
            'fecha_contratacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'defendido': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pago_realizado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'numero_factura': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'fecha_contratacion': 'Fecha de contratación',
            'defendido': 'Defendido el trabajo de titulación',
            'pago_realizado': 'Pago realizado al tutor',
            'numero_factura': 'N° Factura',
            'observaciones': 'Observaciones (si no está pagado)',
        }


class EstudianteProgramaGestionForm(forms.ModelForm):
    class Meta:
        model = EstudianteProgramaGestion
        fields = [
            'pago_inscripcion', 'pago_matricula', 'pago_primera_colegiatura', 'pago_segunda_colegiatura',
            'cuotas_pagadas',
            'modalidad', 'fecha_rubrica_aprobada',
            'tutor_resolucion', 'tutor_resolucion_fecha', 'tutor_contratado',
            'avance_porcentaje',
            'fecha_sustentacion_oral', 'fecha_aprob_complexivo',
            'estado_titulo',
        ]
        widgets = {
            'pago_inscripcion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pago_matricula': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pago_primera_colegiatura': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pago_segunda_colegiatura': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cuotas_pagadas': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '10'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'}),
            'fecha_rubrica_aprobada': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tutor_resolucion': forms.TextInput(attrs={'class': 'form-control'}),
            'tutor_resolucion_fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tutor_contratado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'avance_porcentaje': forms.Select(attrs={'class': 'form-select'}),
            'fecha_sustentacion_oral': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_aprob_complexivo': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado_titulo': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'pago_inscripcion': 'Inscripción pagada',
            'pago_matricula': 'Matrícula pagada',
            'pago_primera_colegiatura': '1ª colegiatura pagada',
            'pago_segunda_colegiatura': '2ª colegiatura pagada',
            'cuotas_pagadas': 'Cuotas pagadas (0 a 10)',
            'modalidad': 'Modalidad de titulación',
            'fecha_rubrica_aprobada': 'Rúbrica de tema aprobada (fecha)',
            'tutor_resolucion': 'Resolución de tutor',
            'tutor_resolucion_fecha': 'Fecha de resolución',
            'tutor_contratado': 'Tutor contratado',
            'avance_porcentaje': 'Porcentaje de avance',
            'fecha_sustentacion_oral': 'Sustentación oral (fecha)',
            'fecha_aprob_complexivo': 'Aprobación exámen complexivo (fecha)',
            'estado_titulo': 'Estado de título',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nunca requerido: el modelo ya valida rango y la vista lo normaliza a 0 si aplica
        self.fields['cuotas_pagadas'].required = False
