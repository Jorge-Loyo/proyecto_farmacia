from django import forms
from .models import Medicamento, Equivalencia

class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        # Simplemente añadimos 'id_alfabeta' al principio de la lista
        fields = ['id_alfabeta', 'nombre_comercial', 'laboratorio', 'monodroga', 'precio_caja', 'precio_unitario']

class EquivalenciaForm(forms.ModelForm):
    class Meta:
        model = Equivalencia
        # Excluimos el campo de la relación, ya que no se edita directamente
        exclude = ['medicamento_alfabeta']