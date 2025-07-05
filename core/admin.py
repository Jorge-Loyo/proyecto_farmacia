from django.contrib import admin
from .models import Laboratorio, Monodroga, Medicamento, Equivalencia, RegistroCarga
from import_export.admin import ImportExportModelAdmin

@admin.register(Medicamento)
# El cambio clave es heredar de 'ImportExportModelAdmin'
class MedicamentoAdmin(ImportExportModelAdmin):
    list_display = ('id_alfabeta', 'nombre_comercial', 'laboratorio', 'monodroga', 'estado')
    search_fields = ('nombre_comercial', 'id_alfabeta')
    list_filter = ('laboratorio', 'estado',)
    list_per_page = 25

@admin.register(Laboratorio)
class LaboratorioAdmin(ImportExportModelAdmin):
    search_fields = ('nombre',)

@admin.register(Monodroga)
class MonodrogaAdmin(ImportExportModelAdmin):
    search_fields = ('nombre',)

@admin.register(Equivalencia)
class EquivalenciaAdmin(ImportExportModelAdmin):
    list_display = ('medicamento_alfabeta',)
    search_fields = ('medicamento_alfabeta__nombre_comercial',)


# Registra los demás modelos para que aparezcan en el admin
admin.site.register(RegistroCarga)