import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

# Importa todos los modelos y la excepción personalizada
from core.models import Laboratorio, Monodroga, Medicamento, Equivalencia, RegistroCarga, HistorialPrecio

class CargaDatosException(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Errores de validación durante la carga.")

class Command(BaseCommand):
    help = 'Actualiza y valida registros desde el archivo XLSX, protegiendo la cantidad y calculando precios.'

    def handle(self, *args, **kwargs):
        file_path = 'data/ALFABETA PUBLICADO EN OCTUBRE.xlsx'
        
        # 1. Cargar DataFrames
        df_lab = pd.read_excel(file_path, sheet_name='Laboratorio').dropna(subset=['Codigo']).drop_duplicates(subset=['Codigo'])
        df_mono = pd.read_excel(file_path, sheet_name='Monodroga').dropna(subset=['Cod Monodroga', 'buscar']).drop_duplicates(subset=['buscar'])
        df_med = pd.read_excel(file_path, sheet_name='Medicamentos').dropna(subset=['Cod Alfabeta'])

        # 2. Validar el archivo Excel antes de tocar la base de datos
        validation_errors = []
        lab_ids_validos = set(df_lab['Codigo'].astype(int))
        mono_ids_validos = set(df_mono['Cod Monodroga'].astype(int))

        for index, row in df_med.iterrows():
            if int(row['Cod Laboratorio']) not in lab_ids_validos:
                validation_errors.append(f"Fila {index+2} (Medicamentos): El Laboratorio con código {int(row['Cod Laboratorio'])} no existe en la hoja 'Laboratorio'.")
            if int(row['Cod Monodroga']) not in mono_ids_validos:
                validation_errors.append(f"Fila {index+2} (Medicamentos): La Monodroga con código {int(row['Cod Monodroga'])} no existe en la hoja 'Monodroga'.")

        if validation_errors:
            raise CargaDatosException(validation_errors)

        # 3. Iniciar transacción en la base de datos
        with transaction.atomic():
            # Sincronizar Laboratorios y Monodrogas
            for _, row in df_lab.iterrows():
                Laboratorio.objects.update_or_create(id=int(row['Codigo']), defaults={'nombre': row['Descripcion']})
            for _, row in df_mono.iterrows():
                Monodroga.objects.update_or_create(id=int(row['Cod Monodroga']), defaults={'nombre': row['buscar']})

            nuevos = 0
            actualizados = 0
            for _, row in df_med.iterrows():
                try:
                    medicamento = Medicamento.objects.get(pk=int(row['Cod Alfabeta']))
                    
                    # SI EXISTE: Lógica de Actualización
                    medicamento.nombre_comercial = row['Marca +Presenta']
                    medicamento.laboratorio_id = int(row['Cod Laboratorio'])
                    medicamento.monodroga_id = int(row['Cod Monodroga'])
                    medicamento.precio_caja = Decimal(str(row['Precio x Caja']).replace(',', '.'))
                    medicamento.estado = int(row.get('Cod AB', 0))
                    
                    # Condición para la cantidad (con la indentación correcta)
                    if not medicamento.cantidad:
                        medicamento.cantidad = int(row.get('Cantidad', 1))
                    
                    medicamento.save()
                    actualizados += 1

                except Medicamento.DoesNotExist:
                    # SI NO EXISTE: Lógica de Creación
                    nuevo_medicamento = Medicamento(
                        id_alfabeta=int(row['Cod Alfabeta']),
                        nombre_comercial=row['Marca +Presenta'],
                        laboratorio_id=int(row['Cod Laboratorio']),
                        monodroga_id=int(row['Cod Monodroga']), # <-- Esta línea faltaba en tu código
                        precio_caja=Decimal(str(row['Precio x Caja']).replace(',', '.')),
                        estado=int(row.get('Cod AB', 0)),
                        cantidad=int(row.get('Cantidad', 1))
                    )
                    nuevo_medicamento.save()
                    Equivalencia.objects.create(medicamento_alfabeta=nuevo_medicamento)
                    HistorialPrecio.objects.create(medicamento=nuevo_medicamento, precio_caja=nuevo_medicamento.precio_caja, precio_unitario=nuevo_medicamento.precio_unitario)
                    nuevos += 1
            
            self.stdout.write(self.style.SUCCESS(f'Sincronización completa: {nuevos} medicamentos creados, {actualizados} actualizados.'))
            RegistroCarga.objects.update_or_create(fuente='ALFABETA', defaults={'fecha_carga': timezone.now()})