from django import forms
from .models import ReactivosMultipleChoice, ComponenteRAE, SubcomponenteRAE, SubcomponenteModuloRAE
from django.forms import inlineformset_factory
from django.contrib.auth import get_user_model
from tinymce.widgets import TinyMCE
from programasposgrado.models import Modulos


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
        def clean_enunciado(self):
            enunciado = self.cleaned_data.get('enunciado')
            if ReactivosMultipleChoice.objects.filter(enunciado=enunciado).exists():
                raise forms.ValidationError("Ya existe un reactivo con este enunciado.")
            return enunciado

class ComponenteRAEForm(forms.ModelForm):
    class Meta:
        model = ComponenteRAE
        fields = ['nombre', 'orden', 'peso', 'preguntas_sugeridas', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'preguntas_sugeridas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class SubcomponenteRAEForm(forms.ModelForm):
    class Meta:
        model = SubcomponenteRAE
        fields = ['nombre', 'orden', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


SubcomponenteFormSet = inlineformset_factory(
    ComponenteRAE,
    SubcomponenteRAE,
    form=SubcomponenteRAEForm,
    fields=['nombre', 'orden', 'observaciones'],
    extra=1,
    can_delete=True
)


class SubcomponenteAsignarModulosForm(forms.Form):
    """
    Multiselección de módulos por subcomponente, filtrando por maestría del programa
    y excluyendo los ya asignados a otros subcomponentes del mismo programa.
    """
    modulos = forms.ModelMultipleChoiceField(
        queryset=Modulos.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 12})
    )

    def __init__(self, *args, **kwargs):
        subcomponente = kwargs.pop('subcomponente')
        super().__init__(*args, **kwargs)
        self.subcomponente = subcomponente
        programa = subcomponente.componente.programa

        base_qs = Modulos.objects.filter(
            maestria=programa.maestria
        ).order_by('codificacion', 'nombre')

        ya_asignados = SubcomponenteModuloRAE.objects.filter(
            subcomponente__componente__programa=programa
        ).exclude(subcomponente=subcomponente).values_list('modulo_id', flat=True)

        self.fields['modulos'].queryset = base_qs.exclude(id__in=list(ya_asignados))

        actuales = SubcomponenteModuloRAE.objects.filter(
            subcomponente=subcomponente
        ).values_list('modulo_id', flat=True)
        self.initial['modulos'] = list(actuales)

    def save(self):
        seleccionados = list(self.cleaned_data.get('modulos', []))
        sub = self.subcomponente

        # Eliminar los que ya no estén seleccionados
        SubcomponenteModuloRAE.objects.filter(subcomponente=sub).exclude(
            modulo__in=seleccionados
        ).delete()

        # Crear los nuevos
        existentes = set(
            SubcomponenteModuloRAE.objects.filter(subcomponente=sub)
            .values_list('modulo_id', flat=True)
        )
        for modulo in seleccionados:
            if modulo.id not in existentes:
                SubcomponenteModuloRAE.objects.create(subcomponente=sub, modulo=modulo)