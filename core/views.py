import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db import models
from django.contrib import messages
from django.core.management import call_command
from django.core.files.storage import FileSystemStorage
import io
# Importa todos los modelos y formularios que vamos a usar
from .models import Medicamento, Laboratorio, Monodroga, RegistroCarga, Equivalencia, HistorialPrecio
from .forms import UploadFileForm, MedicamentoForm, EquivalenciaForm

# Importamos la excepción personalizada para el manejo de errores
from core.management.commands.cargar_datos import CargaDatosException

def dashboard(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fuente = form.cleaned_data['fuente']
            archivo = form.cleaned_data['archivo']
            if fuente == 'ALFABETA':
                fs = FileSystemStorage(location='data/')
                filename = 'ALFABETA PUBLICADO EN OCTUBRE.xlsx'
                if fs.exists(filename):
                    try:
                        fs.delete(filename)
                    except PermissionError:
                        messages.error(request, 'Error de Permiso: El archivo Excel está abierto. Por favor, ciérrelo y vuelva a intentarlo.')
                        return redirect('dashboard')
                fs.save(filename, archivo)
                try:
                    call_command('cargar_datos')
                    messages.success(request, '¡Éxito! El archivo fue validado y cargado correctamente.')
                except CargaDatosException as e:
                    messages.error(request, 'El archivo no se pudo cargar. Errores encontrados:')
                    for error in e.errors[:10]:
                        messages.error(request, f'- {error}')
                except Exception as e:
                    messages.error(request, f'Error Inesperado: {e}')
            return redirect('dashboard')
    else:
        form = UploadFileForm()

    total_medicamentos = Medicamento.objects.count()
    total_laboratorios = Laboratorio.objects.count()
    total_monodrogas = Monodroga.objects.count()
    fuentes = ['ALFABETA', 'CEO', 'HMC', 'HNPM', 'HMCM', 'HMRP', 'HMRC']
    fechas_carga = {}
    for f in fuentes:
        registro = RegistroCarga.objects.filter(fuente=f).first()
        fechas_carga[f] = registro.fecha_carga if registro else None
    context = {
        'form': form,
        'total_medicamentos': total_medicamentos,
        'total_laboratorios': total_laboratorios,
        'total_monodrogas': total_monodrogas,
        'fechas_carga': fechas_carga,
    }
    return render(request, 'core/dashboard.html', context)

def lista_medicamentos(request):
    medicamentos_list = Medicamento.objects.select_related('laboratorio', 'monodroga').all().order_by('nombre_comercial')
    query = request.GET.get('q', '')
    if query:
        q_objects = models.Q(nombre_comercial__icontains=query)
        if query.isdigit():
            q_objects |= models.Q(id_alfabeta=int(query))
        medicamentos_list = medicamentos_list.filter(q_objects)
    paginator = Paginator(medicamentos_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'core/lista_medicamentos.html', context)

def crear_medicamento(request):
    if request.method == 'POST':
        medicamento_form = MedicamentoForm(request.POST)
        if medicamento_form.is_valid():
            medicamento_nuevo = medicamento_form.save()
            Equivalencia.objects.create(medicamento_alfabeta=medicamento_nuevo)
            messages.success(request, f'El medicamento "{medicamento_nuevo.nombre_comercial}" ha sido creado con éxito.')
            return redirect('lista_medicamentos')
    else:
        medicamento_form = MedicamentoForm()
    context = {
        'medicamento_form': medicamento_form,
    }
    return render(request, 'core/crear_medicamento.html', context)

def editar_medicamento(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)
    equivalencia = get_object_or_404(Equivalencia, pk=pk)
    if request.method == 'POST':
        medicamento_form = MedicamentoForm(request.POST, instance=medicamento)
        equivalencia_form = EquivalenciaForm(request.POST, instance=equivalencia)
        if medicamento_form.is_valid() and equivalencia_form.is_valid():
            medicamento_form.save()
            equivalencia_form.save()
            messages.success(request, 'Los cambios se han guardado correctamente.')
            return redirect('lista_medicamentos')
    else:
        medicamento_form = MedicamentoForm(instance=medicamento)
        equivalencia_form = EquivalenciaForm(instance=equivalencia)
    context = {
        'medicamento_form': medicamento_form,
        'equivalencia_form': equivalencia_form,
        'medicamento': medicamento,
    }
    return render(request, 'core/editar_medicamento.html', context)

def eliminar_medicamento(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)
    if request.method == 'POST':
        nombre_medicamento = medicamento.nombre_comercial
        medicamento.delete()
        messages.success(request, f'El medicamento "{nombre_medicamento}" ha sido eliminado.')
        return redirect('lista_medicamentos')
    context = {
        'medicamento': medicamento
    }
    return render(request, 'core/eliminar_medicamento_confirm.html', context)

def exportar_a_excel(request):
    medicamentos = Medicamento.objects.all()
    laboratorios = Laboratorio.objects.all()
    monodrogas = Monodroga.objects.all()

    df_med = pd.DataFrame(list(medicamentos.values(
        'id_alfabeta', 'nombre_comercial', 'laboratorio_id', 'monodroga_id', 
        'precio_caja', 'precio_unitario', 'estado' # Incluimos el campo 'estado'
    )))
    df_lab = pd.DataFrame(list(laboratorios.values('id', 'nombre')))
    df_mono = pd.DataFrame(list(monodrogas.values('id', 'nombre')))

    # Renombramos las columnas para que el Excel tenga el formato original
    df_med.rename(columns={
        'id_alfabeta': 'Cod Alfabeta', 
        'nombre_comercial': 'Marca +Presenta', 
        'laboratorio_id': 'Cod Laboratorio', 
        'monodroga_id': 'Cod Monodroga', 
        'precio_caja': 'Precio x Caja', 
        'precio_unitario': 'Precio Unitario',
        'estado': 'Cod AB' # CORRECCIÓN: Renombramos la columna 'estado' a 'Cod AB'
    }, inplace=True)
    df_lab.rename(columns={'id': 'Codigo', 'nombre': 'Descripcion'}, inplace=True)
    df_mono.rename(columns={'id': 'Cod Monodroga', 'nombre': 'buscar'}, inplace=True)
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Base_Medicamentos_Actualizada.xlsx"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df_med.to_excel(writer, sheet_name='Medicamentos', index=False)
        df_lab.to_excel(writer, sheet_name='Laboratorio', index=False)
        df_mono.to_excel(writer, sheet_name='Monodroga', index=False)

    return response