from django import forms
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from .models import ContratosDocentes, ContratoTutor, ContratoCoordinador
from programasposgrado.models import ProgramaPosgrado, ProgramaPosgradoEM


# =========================================================
# DOCENTES
# (Tu create maneja docente/programa/modulo por POST directo,
#  por eso aquí solo validamos lo demás)
# =========================================================
class ContratosDocentesForm(forms.ModelForm):
    class Meta:
        model = ContratosDocentes
        fields = [
            'horasacademicas', 'valorxhora', 'certificacionpresupuestaria',
            'fechacertificacionpresupuestaria', 'plazo', 'numerocontrato',
            'numeromemorandotthh', 'tipopersonalacademico', 'adenda',
            'observaciones', 'urldocumento'
        ]
        widgets = {
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
            'tipopersonalacademico': forms.Select(attrs={'class': 'form-control'}),
            'adenda': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
            'urldocumento': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
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

        # formatos de fecha
        self.fields['fechacertificacionpresupuestaria'].input_formats = ['%Y-%m-%d']

        # opcionales
        if 'adenda' in self.fields:
            self.fields['adenda'].required = False
        if 'observaciones' in self.fields:
            self.fields['observaciones'].required = False
        if 'urldocumento' in self.fields:
            self.fields['urldocumento'].required = False
        if not self.instance.pk:
            anio = datetime.now().year
            self.fields['numerocontrato'].initial = 'SP-DATH-UNACH-'
            self.fields['numeromemorandotthh'].initial = f'-DATH-UNACH-{anio}'

# =========================================================
# Helpers: convertir "M-12" / "EM-5" -> content_type + object_id
# =========================================================
def _mix_to_ct_and_id(programa_mix: str):
    """
    Recibe "PP-12" o "EM-5" y devuelve (ContentType, object_id, tipo)
    """
    if not programa_mix or '-' not in programa_mix:
        return None, None, None

    tipo, obj_id = programa_mix.split('-', 1)
    tipo = (tipo or '').strip()

    try:
        obj_id = int(obj_id)
    except ValueError:
        return None, None, None

    if tipo == 'PP':
        ct = ContentType.objects.get_for_model(ProgramaPosgrado)
    elif tipo == 'EM':
        ct = ContentType.objects.get_for_model(ProgramaPosgradoEM)
    else:
        return None, None, None

    return ct, obj_id, tipo

# =========================================================
# TUTORES (con GenericForeignKey a programa)
# =========================================================
class ContratoTutorForm(forms.ModelForm):
    # Campo "bonito" para escoger programa (M/EM) en un solo select.
    # El view/HTML lo alimenta; el form lo transforma a ct + id.
    programa_mix = forms.ChoiceField(
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ContratoTutor
        fields = [
            'tutor',
            'maestrante',
            'programa_mix',  # <-- NO es del modelo, pero se procesa
            'plazo',
            'certificacionpresupuestaria',
            'fechacertificacionpresupuestaria',
            'valorcontrato',
            'numerocontrato',
            'numeromemorandotthh',
            'tipopersonalacademico',
            'adenda',
            'observaciones',
            'urldocumento',
        ]
        widgets = {
            'tutor': forms.Select(attrs={'class': 'form-control'}),
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
            'tipopersonalacademico': forms.Select(attrs={'class': 'form-control'}),
            'adenda': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control'}),
            'urldocumento': forms.URLInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'tutor': 'Tutor',
            'maestrante': 'Maestrante',
            'programa_mix': 'Programa de Posgrado',
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
        # Recibe choices desde el view para no acoplar aquí.
        programa_choices = kwargs.pop('programa_choices', None)

        super().__init__(*args, **kwargs)

        self.fields['fechacertificacionpresupuestaria'].input_formats = ['%Y-%m-%d']

        # opcionales
        self.fields['adenda'].required = False
        self.fields['observaciones'].required = False
        self.fields['urldocumento'].required = False

        # Cargar choices del select "programa_mix"
        if programa_choices is not None:
            self.fields['programa_mix'].choices = programa_choices
        else:
            # fallback mínimo (para no romper si te olvidas pasarlo)
            self.fields['programa_mix'].choices = [('', 'Seleccione un programa')]

    def clean(self):
        cleaned = super().clean()

        programa_mix = cleaned.get('programa_mix')
        ct, obj_id, tipo = _mix_to_ct_and_id(programa_mix)

        if not ct or not obj_id or not tipo:
            self.add_error('programa_mix', 'Seleccione un programa válido.')
            return cleaned

        # Validación de existencia
        Model = ct.model_class()
        if not Model.objects.filter(id=obj_id).exists():
            self.add_error('programa_mix', 'El programa seleccionado no existe.')
            return cleaned

        # Guardar en el instance (campos reales del modelo)
        self.instance.programa_content_type = ct
        self.instance.programa_object_id = obj_id

        # Si tu modelo mantiene programa_tipo, lo seteamos automáticamente
        # if hasattr(self.instance, 'programa_tipo'):
        #     self.instance.programa_tipo = tipo

        return cleaned


# =========================================================
# COORDINADORES (con GenericForeignKey a programa)
# =========================================================
class ContratoCoordinadorForm(forms.ModelForm):
    programa_mix = forms.ChoiceField(
        choices=[],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = ContratoCoordinador
        fields = [
            'coordinador',
            'programa_mix',
            'certificacionpresupuestaria',
            'fechacertificacionpresupuestaria',
            'plazo',
            'fechainicio',
            'fechafin',
            'honorario',
            'numerocontrato',
            'cargo',
            'noactasseleccion',
            'oficioentregadoporth',
            'modalidadcontractuar',
            'observaciones',
            'urldocumento',
        ]
        widgets = {
            'certificacionpresupuestaria': forms.TextInput(attrs={'class': 'form-control'}),
            'fechacertificacionpresupuestaria': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'plazo': forms.TextInput(attrs={'class': 'form-control'}),
            'fechainicio': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'fechafin': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'honorario': forms.NumberInput(attrs={'class': 'form-control'}),
            'numerocontrato': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'noactasseleccion': forms.TextInput(attrs={'class': 'form-control'}),
            'oficioentregadoporth': forms.TextInput(attrs={'class': 'form-control'}),
            'modalidadcontractuar': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'urldocumento': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        programa_choices = kwargs.pop('programa_choices', None)
        super().__init__(*args, **kwargs)

        # opcionales
        self.fields['observaciones'].required = False
        self.fields['urldocumento'].required = False
        self.fields['plazo'].required = False
        self.fields['fechainicio'].required = False
        self.fields['fechafin'].required = False

        if programa_choices is not None:
            self.fields['programa_mix'].choices = programa_choices
        else:
            self.fields['programa_mix'].choices = [('', 'Seleccione un programa')]


    def clean(self):
        cleaned = super().clean()

        programa_mix = cleaned.get('programa_mix')
        ct, obj_id, _tipo = _mix_to_ct_and_id(programa_mix)  # <-- ahora sí

        if not ct or not obj_id:
            self.add_error('programa_mix', 'Seleccione un programa válido.')
            return cleaned

        Model = ct.model_class()
        if not Model.objects.filter(id=obj_id).exists():
            self.add_error('programa_mix', 'El programa seleccionado no existe.')
            return cleaned

        # setear SOLO campos reales
        self.instance.programa_content_type = ct
        self.instance.programa_object_id = obj_id

        return cleaned