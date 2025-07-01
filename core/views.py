from django.shortcuts import render
from django.core.paginator import Paginator
from django.db import models # Importante para la búsqueda con Q
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db import models
from .models import Medicamento, Laboratorio, Monodroga, RegistroCarga, Equivalencia
from .forms import MedicamentoForm, EquivalenciaForm

# Importa todos los modelos que necesitas usar
from .models import Medicamento, Laboratorio, Monodroga, RegistroCarga

def dashboard(request):
    """
    Prepara los datos para el dashboard principal.
    """
    total_medicamentos = Medicamento.objects.count()
    total_laboratorios = Laboratorio.objects.count()
    total_monodrogas = Monodroga.objects.count()

    # Lógica para obtener las fechas de la última carga
    fuentes = ['ALFABETA', 'CEO', 'HMC', 'HNPM', 'HMCM', 'HMRP', 'HMRC']
    fechas_carga = {}
    for f in fuentes:
        registro = RegistroCarga.objects.filter(fuente=f).first()
        fechas_carga[f] = registro.fecha_carga if registro else None

    context = {
        'total_medicamentos': total_medicamentos,
        'total_laboratorios': total_laboratorios,
        'total_monodrogas': total_monodrogas,
        'fechas_carga': fechas_carga,
    }
    
    return render(request, 'core/dashboard.html', context)


def lista_medicamentos(request):
    """
    Muestra una lista paginada de medicamentos con un buscador inteligente.
    """
    medicamentos_list = Medicamento.objects.select_related('laboratorio', 'monodroga').all().order_by('nombre_comercial')

    query = request.GET.get('q', '')
    if query:
        # Creamos un objeto de búsqueda base para el nombre
        q_objects = models.Q(nombre_comercial__icontains=query)

        # Si el texto de búsqueda contiene solo dígitos, añadimos la búsqueda por ID
        if query.isdigit():
            q_objects |= models.Q(id_alfabeta=int(query))

        # Aplicamos el filtro final
        medicamentos_list = medicamentos_list.filter(q_objects)

    paginator = Paginator(medicamentos_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'core/lista_medicamentos.html', context)

def editar_medicamento(request, pk):
    # Obtenemos el medicamento que se quiere editar, o un error 404 si no existe
    medicamento = get_object_or_404(Medicamento, pk=pk)
    # Obtenemos su equivalencia asociada
    equivalencia = get_object_or_404(Equivalencia, pk=pk)

    # Si el método es POST, significa que el usuario envió el formulario
    if request.method == 'POST':
        # Creamos instancias de los formularios con los datos enviados
        medicamento_form = MedicamentoForm(request.POST, instance=medicamento)
        equivalencia_form = EquivalenciaForm(request.POST, instance=equivalencia)

        # Verificamos si ambos formularios son válidos
        if medicamento_form.is_valid() and equivalencia_form.is_valid():
            medicamento_form.save() # Guardamos los cambios del medicamento
            equivalencia_form.save() # Guardamos los cambios de la equivalencia
            # Redirigimos al usuario de vuelta a la lista de medicamentos
            return redirect('lista_medicamentos')
    else:
        # Si el método es GET, creamos formularios vacíos con los datos actuales
        medicamento_form = MedicamentoForm(instance=medicamento)
        equivalencia_form = EquivalenciaForm(instance=equivalencia)

    context = {
        'medicamento_form': medicamento_form,
        'equivalencia_form': equivalencia_form,
        'medicamento': medicamento, # Enviamos el objeto para mostrar su nombre
    }
    return render(request, 'core/editar_medicamento.html', context)



def eliminar_medicamento(request, pk):
    # Buscamos el medicamento que se quiere eliminar
    medicamento = get_object_or_404(Medicamento, pk=pk)

    # Si el método es POST, significa que el usuario confirmó la eliminación
    if request.method == 'POST':
        medicamento.delete() # ¡Adiós, medicamento!
        # Redirigimos a la lista de medicamentos
        return redirect('lista_medicamentos')

    # Si el método es GET, solo mostramos la página de confirmación
    context = {
        'medicamento': medicamento
    }
    return render(request, 'core/eliminar_medicamento_confirm.html', context)



def crear_medicamento(request):
    if request.method == 'POST':
        # Creamos instancias de los formularios con los datos enviados
        medicamento_form = MedicamentoForm(request.POST)
        equivalencia_form = EquivalenciaForm(request.POST) # Aunque no se use, es bueno mantenerlo por si se añaden campos

        if medicamento_form.is_valid():
            # Primero, guardamos el medicamento para obtener un ID
            medicamento_nuevo = medicamento_form.save()

            # Luego, creamos su tabla de equivalencia asociada
            Equivalencia.objects.create(medicamento_alfabeta=medicamento_nuevo)

            # Redirigimos a la lista
            return redirect('lista_medicamentos')
    else:
        # Si es GET, mostramos formularios vacíos
        medicamento_form = MedicamentoForm()
        equivalencia_form = EquivalenciaForm()

    context = {
        'medicamento_form': medicamento_form,
        'equivalencia_form': equivalencia_form,
    }
    return render(request, 'core/crear_medicamento.html', context)