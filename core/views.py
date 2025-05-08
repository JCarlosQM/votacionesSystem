from io import BytesIO

import openpyxl
import pandas as pd

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import View

from .forms import CustomLoginForm, CampañaForm, ListaForm, VotanteForm
from .models import Campaña, Lista, Votante, Voto


@login_required
# views.py
def dashboard(request):
    campañas = Campaña.objects.all()  # O la lógica que necesites
    return render(request, 'base_admin.html', {'campañas': campañas})


class CustomLoginView(View):
    template_name = "admin/login.html"

    def get(self, request):
        # Si el usuario ya está autenticado, redirige a la página del dashboard
        if request.user.is_authenticated:
            return redirect('dashboard')  # O redirige a la página correspondiente
        form = CustomLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # Asegúrate de tener la URL 'dashboard' configurada
        return render(request, self.template_name, {'form': form})

# Vista para el dashboard
@login_required
def dashboard_view(request):
    return render(request, 'admin/dashboard.html')  # Asegúrate de tener esta plantilla

@login_required
def actividades_view(request):
    campañas = Campaña.objects.all().order_by('-fecha_inicio')
    return render(request, 'admin/actividades.html', {'campañas': campañas})

@login_required
def crear_campaña(request):
    if request.method == 'POST':
        form = CampañaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La campaña se ha creado correctamente.')
            return redirect('lista_campañas')
        else:
            messages.error(request, 'Hubo un error al crear la campaña. Por favor, verifica los datos.')
    else:
        form = CampañaForm()
    return render(request, 'admin/crear_campaña.html', {'form': form})

@login_required
def lista_campañas(request):
    campañas = Campaña.objects.all().order_by('-id')
    
    if request.method == 'POST':
        form = CampañaForm(request.POST)
        if form.is_valid():
            form.save()
            # Recargar la página con la paginación intacta
            campañas = Campaña.objects.all().order_by('-id')
            paginator = Paginator(Campaña.objects.all(), 3)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            return render(request, 'admin/lista_campañas.html', {
                'campañas': page_obj,
                'form': CampañaForm(),
                'page_obj': page_obj
            })
    else:
        form = CampañaForm()

    # Configurar paginación
    paginator = Paginator(campañas, 3)  # 3 elementos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/lista_campañas.html', {
        'campañas': page_obj,  # Usar page_obj para iterar
        'form': form,
        'page_obj': page_obj,
    })
    
    
@login_required
def editar_campaña(request, id):
    campaña = get_object_or_404(Campaña, id=id)
    if request.method == 'POST':
        campaña.titulo = request.POST.get('titulo')
        campaña.descripcion = request.POST.get('descripcion')
        campaña.fecha_inicio = request.POST.get('fecha_inicio')
        campaña.fecha_fin = request.POST.get('fecha_fin')
        campaña.activa = True if request.POST.get('activa') == 'True' else False
        campaña.save()
        return redirect('lista-campañas')
    return redirect('lista-campañas')


@login_required
def eliminar_campaña(request, id):
    campaña = get_object_or_404(Campaña, id=id)
    if request.method == 'POST':
        campaña.delete()
    return redirect('lista-campañas')

@login_required
def listar_listas_crear(request):
    listas = Lista.objects.all()
    campañas = Campaña.objects.all()

    if request.method == 'POST':
        form = ListaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_listas')
    else:
        form = ListaForm()

    paginator = Paginator(listas, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Crear un formulario inicializado para cada lista en la página actual
    lista_forms = {}
    for lista in page_obj:
        lista_forms[lista.id] = ListaForm(instance=lista)

    return render(request, 'admin/listar_listas.html', {
        'listas': listas,
        'form': form,
        'page_obj': page_obj,
        'campañas': campañas,
        'lista_forms': lista_forms  # Pasar los formularios inicializados
    })
    
    
@login_required
def editar_lista(request, lista_id):
    lista = get_object_or_404(Lista, id=lista_id)

    if request.method == 'POST':
        form = ListaForm(request.POST, request.FILES, instance=lista)
        if form.is_valid():
            # Si no se sube un nuevo logo, mantener el logo existente
            if not request.FILES.get('logo'):
                form.instance.logo = lista.logo
            form.save()
            return redirect('listar_listas')
    else:
        form = ListaForm(instance=lista)

    return render(request, 'admin/listar_listas.html', {
        'form': form,
        'listas': Lista.objects.all(),
        'page_obj': Paginator(Lista.objects.all(), 3).get_page(request.GET.get('page')),
        'campañas': Campaña.objects.all(),
        'lista_forms': {lista.id: ListaForm(instance=lista) for lista in Lista.objects.all()}
    })
    

@login_required
def eliminar_lista(request, id):
    lista = get_object_or_404(Lista, id=id)
    if request.method == 'POST':
        lista.delete()
        messages.success(request, f'La lista "{lista.nombre}" ha sido eliminada correctamente.')
        return redirect('listar_listas')
    return redirect('listar_listas')


#VOTANTES

def panel_votante(request):
    # Obtenemos la campaña activa
    campaña = Campaña.objects.filter(activa=True).order_by('-fecha_inicio').first()

    # Si hay campaña activa, obtenemos sus listas
    listas = campaña.listas.all() if campaña else []

    return render(request, 'votante/panel.html', {
        'campaña': campaña,
        'listas': listas
    })


def votar_lista(request, lista_id):
    if request.method == 'POST':
        dni = request.POST.get('dni')
        lista = get_object_or_404(Lista, id=lista_id)

        # Verificamos si el votante existe
        try:
            votante = Votante.objects.get(dni=dni)
        except Votante.DoesNotExist:
            messages.error(request, "DNI incorrecto. Verifica tus datos.")
            return redirect('panel_votante')

        # Si el votante ya ha votado, mostramos un mensaje
        if votante.ha_votado:
            messages.warning(request, "Ya has emitido tu voto previamente.")
        else:
            # Creamos una instancia de Voto
            voto = Voto.objects.create(votante=votante, lista=lista)

            # Marcamos al votante como que ya votó
            votante.ha_votado = True
            votante.save()

            messages.success(request, f"Voto registrado exitosamente por la lista {lista.nombre}.")

        return redirect('panel_votante')
    
#REPORTES

@login_required
def reportes(request):
    votos = Voto.objects.all()

    # Calcular totales de votos por lista
    lista_votos_dict = {}
    for voto in votos:
        if voto.lista in lista_votos_dict:
            lista_votos_dict[voto.lista] += 1
        else:
            lista_votos_dict[voto.lista] = 1

    # Convertir a lista de tuplas para paginar
    lista_votos_items = list(lista_votos_dict.items())

    # Paginación: 10 por página (puedes cambiarlo)
    paginator = Paginator(lista_votos_items, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obtener primer y último votante
    primer_voto = votos.order_by('fecha').first()
    ultimo_voto = votos.order_by('-fecha').first()
    total_votos = votos.count()

    context = {
        'lista_votos': page_obj,  # page_obj contiene los elementos paginados
        'primer_voto': primer_voto,
        'ultimo_voto': ultimo_voto,
        'total_votos': total_votos,
    }

    return render(request, 'admin/reportes.html', context)

#EXPORTAR EXCEL

@login_required
def exportar_resultados_excel(request):
    # Crear un libro de trabajo de Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Resultados de Votación"

    # Añadir encabezados
    ws.append(['Lista', 'Total de Votos'])

    # Obtener los resultados con la cantidad de votos por lista
    resultados = Lista.objects.annotate(total_votos=Count('voto')).order_by('-total_votos')

    # Añadir los datos a la hoja de trabajo
    for lista in resultados:
        ws.append([lista.nombre, lista.total_votos])

    # Guardar el archivo en memoria
    archivo = BytesIO()
    wb.save(archivo)
    archivo.seek(0)

    # Preparar la respuesta HTTP
    response = HttpResponse(
        archivo.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="resultados_votacion.xlsx"'
    return response

@login_required
def lista_votantes(request):
    # Obtén los parámetros de la consulta
    query = request.GET.get('q', '')
    voto_filter = request.GET.get('voto', '')

    # Filtra los votantes según el DNI o el filtro de "¿Ha votado?"
    votantes = Votante.objects.all().order_by('-created_at')

    if query:
        votantes = votantes.filter(dni__icontains=query)
    
    if voto_filter:
        if voto_filter == 'si':
            votantes = votantes.filter(ha_votado=True)
        elif voto_filter == 'no':
            votantes = votantes.filter(ha_votado=False)

    # Paginación
    paginator = Paginator(votantes, 7)  # 10 votantes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/lista_votante.html', {
        'votantes': page_obj,
        'query': query,
        'voto_filter': voto_filter,
    })

    
@csrf_exempt
@require_POST
@login_required
def eliminar_votante_ajax(request, votante_id):
    try:
        votante = Votante.objects.get(id=votante_id)
        votante.delete()
        return JsonResponse({'success': True})
    except Votante.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Votante no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def crear_votante(request):
    if request.method == 'POST':
        form = VotanteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_votantes')
        else:
            return render(request, 'admin/lista_votante.html', {'form': form})
    return redirect('lista_votantes')

#Importar votantes 

@login_required
def importar_votantes(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            # Leer el archivo Excel
            df = pd.read_excel(excel_file)
            df.columns = [col.strip() for col in df.columns]

            if 'DNI' not in df.columns:
                return JsonResponse({'success': False, 'error': 'El archivo debe contener la columna "DNI"'}, status=400)

            errores = []
            for index, row in df.iterrows():
                raw_dni = row['DNI']

                if pd.isna(raw_dni):
                    errores.append(f'Fila {index+2}: DNI vacío')
                    continue

                dni = str(raw_dni).strip()

                # Quitar decimales si vienen como float (por ejemplo: 12345678.0)
                if '.' in dni:
                    dni = dni.split('.')[0]

                if not dni.isdigit() or len(dni) != 8:
                    errores.append(f'Fila {index+2}: DNI inválido "{dni}"')
                    continue

                Votante.objects.update_or_create(
                    dni=dni,
                    defaults={'ha_votado': False}
                )

            if errores:
                return JsonResponse({'success': False, 'error': 'Errores encontrados en el archivo', 'detalles': errores}, status=400)

            return JsonResponse({'success': True, 'message': 'Votantes importados con éxito'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error al procesar el archivo: {str(e)}'}, status=400)

    return render(request, 'admin/lista_votante.html')

#Limpiar votaciones 

@csrf_exempt
@require_POST
@login_required
def limpiar_votaciones(request):
    try:
        # Eliminar todos los votos
        Voto.objects.all().delete()
        # Actualizar todos los votantes, estableciendo ha_votado a False
        Votante.objects.all().update(ha_votado=False)
        return JsonResponse({'success': True, 'message': 'Votaciones limpiadas con éxito'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
#Gestión de gráfico

@require_GET
@login_required
def obtener_datos_grafico(request):
    try:
        # Obtener el conteo de votos por lista
        votos_por_lista = Voto.objects.values('lista__nombre').annotate(total_votos=models.Count('lista'))
        datos = {
            'labels': [item['lista__nombre'] for item in votos_por_lista],
            'data': [item['total_votos'] for item in votos_por_lista]
        }
        return JsonResponse({'success': True, 'data': datos})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)