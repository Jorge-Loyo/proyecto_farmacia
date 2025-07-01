import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Laboratorio, Monodroga, Medicamento, Equivalencia
from django.db import transaction

class Command(BaseCommand):
    help = 'Carga, limpia y relaciona datos desde un archivo XLSX.'

    def handle(self, *args, **kwargs):
        file_path = 'data/ALFABETA PUBLICADO EN OCTUBRE.xlsx'
        self.stdout.write(self.style.SUCCESS('Iniciando carga final de datos...'))

        # --- 1. PREPARACIÓN DE DATOS ---
        df_lab = pd.read_excel(file_path, sheet_name='Laboratorio').dropna(subset=['Codigo', 'Descripcion']).drop_duplicates(subset=['Codigo'], keep='first')
        
        # Limpia monodrogas por nombre, pero guarda un mapa para resolver relaciones rotas
        df_mono_original = pd.read_excel(file_path, sheet_name='Monodroga').dropna(subset=['Cod Monodroga', 'buscar'])
        df_mono_limpio = df_mono_original.drop_duplicates(subset=['buscar'], keep='first')
        
        mapa_id_a_nombre = df_mono_original.set_index('Cod Monodroga')['buscar']
        mapa_nombre_a_id_canonico = df_mono_limpio.set_index('buscar')['Cod Monodroga']
        
        df_med = pd.read_excel(file_path, sheet_name='Medicamentos').dropna(subset=['Cod Alfabeta', 'Cod Laboratorio', 'Cod Monodroga']).drop_duplicates(subset=['Cod Alfabeta'], keep='first')

        with transaction.atomic():
            self.stdout.write(self.style.WARNING('Limpiando tablas para la carga final...'))
            Equivalencia.objects.all().delete()
            Medicamento.objects.all().delete()
            Monodroga.objects.all().delete()
            Laboratorio.objects.all().delete()

            # --- 2. CARGA MASIVA ---
            Laboratorio.objects.bulk_create([Laboratorio(id=row['Codigo'], nombre=row['Descripcion']) for _, row in df_lab.iterrows()])
            self.stdout.write(self.style.SUCCESS(f'{Laboratorio.objects.count()} laboratorios cargados.'))
            
            Monodroga.objects.bulk_create([Monodroga(id=row['Cod Monodroga'], nombre=row['buscar']) for _, row in df_mono_limpio.iterrows()])
            self.stdout.write(self.style.SUCCESS(f'{Monodroga.objects.count()} monodrogas únicas cargadas.'))

            medicamentos_para_crear = []
            for _, row in df_med.iterrows():
                try:
                    # Lógica para resolver relaciones rotas
                    nombre_mono = mapa_id_a_nombre[row['Cod Monodroga']]
                    id_mono_final = mapa_nombre_a_id_canonico[nombre_mono]

                    medicamentos_para_crear.append(
                        Medicamento(
                            id_alfabeta=int(row['Cod Alfabeta']),
                            nombre_comercial=row['Marca +Presenta'],
                            laboratorio_id=int(row['Cod Laboratorio']),
                            monodroga_id=int(id_mono_final), # Se usa el ID limpio
                            precio_caja=float(str(row['Precio x Caja']).replace(',', '.')),
                            precio_unitario=float(str(row['Precio Unitario']).replace(',', '.'))
                        )
                    )
                except KeyError:
                    # Si un medicamento apunta a un laboratorio o monodroga que no existe en sus respectivas hojas, se ignora.
                    continue
            
            Medicamento.objects.bulk_create(medicamentos_para_crear, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f'{Medicamento.objects.count()} medicamentos cargados.'))

            Equivalencia.objects.bulk_create([Equivalencia(medicamento_alfabeta=med) for med in Medicamento.objects.all()], ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f'{Equivalencia.objects.count()} equivalencias creadas.'))

        self.stdout.write(self.style.SUCCESS('¡ÉXITO TOTAL! Los datos han sido cargados.'))