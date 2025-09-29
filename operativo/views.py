from django.utils import timezone
from directivo import models
from .forms import IntegranteForm
from .models import AcuerdoOperativo, Integrante
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Nota
from .forms import NotaForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json
from reportlab.pdfgen import canvas
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Tus modelos y formularios
from .models import Integrante, Nota, AcuerdoOperativo
from .forms import IntegranteForm

def operativo_view(request):
    fecha_actual = timezone.now()
    return render(request, "operativo/base.html", {"fecha_actual": fecha_actual})

# Vista unificada para mostrar y agregar integrantes
def operativo_view(request):
    # Formulario para agregar integrantes
    if request.method == "POST" and 'agregar_integrante' in request.POST:
        form = IntegranteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('operativo_index')
    else:
        form = IntegranteForm()

    # Traer todos los integrantes existentes
    integrantes = Integrante.objects.all().order_by('area__nombre', 'nombre_completo')

    # Para la búsqueda
    query = request.GET.get('q')
    if query:
        integrantes = integrantes.filter(nombre_completo__icontains=query)

    # Lista de seleccionados vacía al inicio (solo se maneja en JS)
    seleccionados = []

    return render(request, "operativo/base.html", {
        'integrantes': integrantes,
        'form': form,
        'seleccionados': seleccionados,
        'fecha_actual': timezone.now(),
    })
    

def editar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    if request.method == "POST":
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            return redirect('operativo_index')  # o lista_notas si usas esa view
    else:
        form = NotaForm(instance=nota)
    return render(request, 'operativo/partials/desarrollo.html', {'form': form, 'nota': nota})

def lista_notas(request):
    notas = Nota.objects.all().order_by('-fecha_creacion')
    return render(request, 'operativo/partials/desarrollo.html', {'notas': notas})

 # necesario porque usamos fetch con CSRF token
def guardar_todo(request):
    if request.method == "POST":
        data = json.loads(request.body)
        notas = data.get('notas', [])
        for n in notas:
            Nota.objects.create(apartado=n['apartado'], texto=n['texto'])
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

def historial_notas(request):
    # Obtener todas las notas ordenadas por fecha (más reciente primero)
    notas = Nota.objects.all().order_by('-fecha_creacion')
    return render(request, 'modulo/historial_notas.html', {'notas': notas})

def crear_acuerdo_operativo(request):
    return render(request, 'modulo/crear_acuerdo_operativo.html')

def historial_acuerdos(request):
    return render(request, 'modulo/historial_acuerdo_operativa.html')


#logica de crear acuerdo 
def crear_acuerdo_operativo(request):
    integrantes = Integrante.objects.all().order_by('area__nombre', 'nombre_completo')
    unidades = list(range(1, 10))  # Para el dropdown de unidades

    if request.method == "POST":
        filas = request.POST.getlist('numerador')
        unidades_post = request.POST.getlist('unidad')
        acuerdos = request.POST.getlist('acuerdo')
        unidad_paradas = request.POST.getlist('unidad_parada')
        fechas_limite = request.POST.getlist('fecha_limite')
        pendientes = request.POST.getlist('pendiente')
        responsables = request.POST.getlist('responsable')
        avances = request.POST.getlist('porcentaje_avance')

        for i in range(len(filas)):
            AcuerdoOperativo.objects.create(
                numerador=int(filas[i]),
                unidad=int(unidades_post[i]),
                acuerdo=acuerdos[i],
                unidad_parada=(unidad_paradas[i] == 'on') if i < len(unidad_paradas) else False,
                fecha_limite=fechas_limite[i],
                pendiente=(pendientes[i] == 'on') if i < len(pendientes) else True,
                responsable_id=int(responsables[i]),
                porcentaje_avance=int(avances[i])
            )
        return redirect('crear_acuerdo_operativo')

    return render(request, 'modulo/crear_acuerdo_operativo.html', {
        'integrantes': integrantes,
        'fecha_actual': timezone.now(),
        'unidades': unidades
    })
    
def historial_acuerdo_operativo(request):
    # Consultar todos los acuerdos, ordenados por fecha de creación
    acuerdos = AcuerdoOperativo.objects.all().order_by('-fecha_creacion')

    # Búsqueda opcional por numerador, acuerdo o responsable
    query = request.GET.get('q')
    if query:
        acuerdos = acuerdos.filter(
            models.Q(acuerdo__icontains=query) |
            models.Q(numerador__icontains=query) |
            models.Q(responsable__nombre_completo__icontains=query)
        )

    return render(request, 'modulo/historial_acuerdo_operativo.html', {
        'acuerdos': acuerdos,
        'query': query,
    })
    
    
    

def seleccionar_integrantes(request):
    integrantes = Integrante.objects.all().order_by("area__nombre", "nombre_completo")

    if request.method == "POST":
        # Tomar lista de IDs enviados desde el formulario oculto
        seleccionados_ids = request.POST.getlist("integrantes")
        request.session["integrantes_seleccionados"] = [str(i) for i in seleccionados_ids]
        # 👇 Redirige directo a descarga en lugar de recargar la misma página
        return redirect("descarga")

    # Obtener seleccionados de la sesión
    seleccionados_ids = request.session.get("integrantes_seleccionados", [])
    seleccionados = Integrante.objects.filter(id__in=seleccionados_ids)

    return render(request, "modulo/integrantes.html", {
        "integrantes": integrantes,
        "seleccionados": seleccionados,
    })











# Vista principal de descarga
def descarga(request):
    integrantes = Integrante.objects.all().order_by("area__nombre", "nombre_completo")
    notas = Nota.objects.all().order_by("fecha_creacion")
    acuerdos = AcuerdoOperativo.objects.all().order_by("fecha_creacion")
    form = IntegranteForm()

    return render(request, "modulo/descarga.html", {
        "integrantes": integrantes,
        "seleccionados": [],
        "notas": notas,
        "acuerdos": acuerdos,
        "form": form
    })


# Descargar PDF con integrantes, notas y acuerdos seleccionados
def descargar_pdf(request):
    if request.method == "POST":
        integrantes_ids = request.POST.getlist('integrantes')
        notas_ids = request.POST.getlist('notas_seleccionadas')
        acuerdos_ids = request.POST.getlist('acuerdos_seleccionados')

        integrantes = Integrante.objects.filter(id__in=integrantes_ids).order_by("area__nombre", "nombre_completo")
        notas = Nota.objects.filter(id__in=notas_ids)
        acuerdos = AcuerdoOperativo.objects.filter(id__in=acuerdos_ids)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="historial.pdf"'

        pdf = canvas.Canvas(response, pagesize=letter)
        ancho, alto = letter
        y = alto - inch

        # Integrantes
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(inch, y, "Integrantes Seleccionados")
        y -= 0.5 * inch
        pdf.setFont("Helvetica", 12)
        if integrantes.exists():
            for i in integrantes:
                pdf.drawString(inch, y, f"{i.nombre_completo} - {i.puesto} ({i.area.nombre})")
                y -= 0.25 * inch
                if y < inch:
                    pdf.showPage()
                    y = alto - inch
        else:
            pdf.drawString(inch, y, "No hay integrantes seleccionados")
            y -= 0.25 * inch

        # Notas
        y -= 0.3 * inch
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(inch, y, "Notas Seleccionadas")
        y -= 0.5 * inch
        pdf.setFont("Helvetica", 12)
        for nota in notas:
            pdf.drawString(inch, y, f"{nota.get_apartado_display()} - {nota.texto} ({nota.fecha_creacion.strftime('%d/%m/%Y %H:%M')})")
            y -= 0.25 * inch
            if y < inch:
                pdf.showPage()
                y = alto - inch

        # Acuerdos
        y -= 0.3 * inch
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(inch, y, "Acuerdos Seleccionados")
        y -= 0.3 * inch
        pdf.setFont("Helvetica", 12)
        for a in acuerdos:
            pendiente = "Sí" if a.pendiente else "No"
            pdf.drawString(inch, y, f"{a.numerador}. Unidad: {a.unidad} - {a.acuerdo} - Responsable: {a.responsable.nombre_completo} - Fecha límite: {a.fecha_limite.strftime('%d/%m/%Y')} - Pendiente: {pendiente} - Avance: {a.porcentaje_avance}% - Creación: {a.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
            y -= 0.25 * inch
            if y < inch:
                pdf.showPage()
                y = alto - inch

        pdf.save()
        return response

    return HttpResponse("Método no permitido", status=405)