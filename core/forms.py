from django import forms
from .models import Medicamento, Equivalencia

class MedicamentoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Medicamento
        # CORRECCIÓN: Añadimos 'cantidad' a la lista de campos.
        fields = ['id_alfabeta', 'nombre_comercial', 'laboratorio', 'monodroga', 'precio_caja', 'estado', 'cantidad']


class EquivalenciaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Equivalencia
        exclude = ['medicamento_alfabeta']

class UploadFileForm(forms.Form):
    # Definimos las opciones para el selector de fuentes
    FUENTES_CHOICES = [
        ('ALFABETA', 'Alfabeta'),
        # A futuro, aquí se añadirán las otras fuentes
        # ('CEO', 'CEO'),
        # ('HMC', 'HMC'),
    ]

    # Campo para seleccionar qué tipo de archivo se está subiendo
    fuente = forms.ChoiceField(choices=FUENTES_CHOICES, label="Fuente de Datos")
    # Campo para subir el archivo
    archivo = forms.FileField(label="Seleccionar Archivo Excel")