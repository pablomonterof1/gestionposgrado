from django import forms
from .models import AreaConocimiento, SubareaConocimiento, CampoConocimiento, CursoCapacitacion, CursoParticipacion

from django.contrib.auth.models import User


class AreaConocimientoForm(forms.ModelForm):
    class Meta:
        model = AreaConocimiento
        fields = ["codigo", "nombre"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 00, 01, 02 ..."}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del área"}),
        }


class SubareaConocimientoForm(forms.ModelForm):
    class Meta:
        model = SubareaConocimiento
        fields = ["area", "codigo", "nombre"]
        widgets = {
            "area": forms.Select(attrs={"class": "form-select"}),
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 001, 002 ..."}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de la subárea"}),
        }


class CampoConocimientoForm(forms.ModelForm):
    class Meta:
        model = CampoConocimiento
        fields = ["subarea", "codigo", "nombre"]
        widgets = {
            "subarea": forms.Select(attrs={"class": "form-select"}),
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: 0011, 0111 ..."}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del campo"}),
        }


class CursoCapacitacionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostrar nombres completos en el combo de facilitador interno
        self.fields['facilitador'].label_from_instance = (
            lambda obj: f"{obj.get_full_name()} ({obj.username})"
            if obj.get_full_name()
            else obj.username
        )

    class Meta:
        model = CursoCapacitacion
        fields = [
            "nombre",
            "area", "subarea", "campo",
            "dirigido_a", "carrera",
            "fecha_inicio", "fecha_fin", "horario",
            "horas_totales", "num_docentes_dirigido",
            "interno_externo",
            "facilitador",
            "facilitador_nombres", "facilitador_cedula",
            "financiamiento", "presupuesto_monto",
            "modalidad", "lugar",
            "activo",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),

            "area": forms.Select(attrs={"class": "form-select"}),
            "subarea": forms.Select(attrs={"class": "form-select"}),
            "campo": forms.Select(attrs={"class": "form-select"}),

            "dirigido_a": forms.TextInput(attrs={"class": "form-control"}),
            "carrera": forms.TextInput(attrs={"class": "form-control"}),

            "fecha_inicio": forms.DateInput(
                format='%Y-%m-%d',
                attrs={"class": "form-control", "type": "date"}
            ),
            "fecha_fin": forms.DateInput(
                format='%Y-%m-%d',
                attrs={"class": "form-control", "type": "date"}
            ),
            "horario": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: 08h00 a 12h00"
            }),

            "horas_totales": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "num_docentes_dirigido": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0
            }),

            "interno_externo": forms.Select(attrs={"class": "form-select"}),

            "facilitador": forms.Select(attrs={"class": "form-select"}),
            "facilitador_nombres": forms.TextInput(attrs={"class": "form-control"}),
            "facilitador_cedula": forms.TextInput(attrs={"class": "form-control"}),

            "financiamiento": forms.Select(attrs={"class": "form-select"}),
            "presupuesto_monto": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),

            "modalidad": forms.Select(attrs={"class": "form-select"}),
            "lugar": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: VIRTUAL / Aula 3 / Zoom"
            }),

            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned = super().clean()

        # =========================
        # Validación jerárquica
        # =========================
        area = cleaned.get("area")
        subarea = cleaned.get("subarea")
        campo = cleaned.get("campo")

        if area and subarea and subarea.area_id != area.id:
            self.add_error(
                "subarea",
                "La subárea seleccionada no pertenece al área elegida."
            )

        if subarea and campo and campo.subarea_id != subarea.id:
            self.add_error(
                "campo",
                "El campo seleccionado no pertenece a la subárea elegida."
            )

        # =========================
        # Validación facilitador
        # =========================
        interno_externo = cleaned.get("interno_externo")
        facilitador = cleaned.get("facilitador")
        nombres = cleaned.get("facilitador_nombres")
        cedula = cleaned.get("facilitador_cedula")

        if interno_externo == "interno":
            if not facilitador:
                self.add_error(
                    "facilitador",
                    "Debe seleccionar un facilitador interno."
                )

            # Limpieza defensiva
            cleaned["facilitador_nombres"] = None
            cleaned["facilitador_cedula"] = None

        elif interno_externo == "externo":
            if facilitador:
                self.add_error(
                    "facilitador",
                    "No debe seleccionar un usuario si el facilitador es externo."
                )

            if not nombres:
                self.add_error(
                    "facilitador_nombres",
                    "Debe ingresar los nombres del facilitador externo."
                )

            if not cedula:
                self.add_error(
                    "facilitador_cedula",
                    "Debe ingresar la cédula del facilitador externo."
                )

        return cleaned
    

# =========================
# Participación y resultados
# =========================

class MatricularParticipantesCursoForm(forms.Form):
    docentes = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(perfilusuario__rol=2).order_by("last_name", "first_name"),
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": "14"}),
        required=True,
        label="Docentes"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["docentes"].label_from_instance = (
            lambda u: f"{u.get_full_name()} ({u.username})" if u.get_full_name() else u.username
        )


class CursoResultadoForm(forms.ModelForm):
    class Meta:
        model = CursoParticipacion
        fields = ["porcentaje_asistencia", "nota_final", "estado_resultado"]
        widgets = {
            "porcentaje_asistencia": forms.NumberInput(attrs={
                "class": "form-control", "step": "0.01", "min": 0, "max": 100
            }),
            "nota_final": forms.NumberInput(attrs={
                "class": "form-control", "step": "0.01", "min": 0, "max": 10
            }),
            "estado_resultado": forms.Select(attrs={"class": "form-select"}),
        }