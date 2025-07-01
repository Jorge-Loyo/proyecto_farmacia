from django.contrib import admin
from .models import Laboratorio, Monodroga, Medicamento, Equivalencia, RegistroCarga
from import_export.admin import ImportExportModelAdmin

@admin.register(Medicamento)
class MedicamentoAdmin(ImportExportModelAdmin):
    list_display = ('id_alfabeta', 'nombre_comercial', 'laboratorio', 'monodroga')
    search_fields = ('nombre_comercial', 'id_alfabeta')
    list_filter = ('laboratorio',)

# Registra los demás modelos para que aparezcan en el panel
admin.site.register(Laboratorio, ImportExportModelAdmin)
admin.site.register(Monodroga, ImportExportModelAdmin)
admin.site.register(Equivalencia, ImportExportModelAdmin)
admin.site.register(RegistroCarga)