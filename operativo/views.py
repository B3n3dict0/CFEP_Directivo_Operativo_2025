from datetime import date
import json
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone

from xhtml2pdf import pisa
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

from directivo import models
from .forms import IntegranteForm, NotaForm
from .models import AcuerdoOperativo, Integrante, Nota


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
            return redirect('operativo_index')
    else:
        form = NotaForm(instance=nota)
    return render(request, 'operativo/partials/desarrollo.html', {'form': form, 'nota': nota})


def lista_notas(request):
    notas = Nota.objects.all().order_by('-fecha_creacion')
    return render(request, 'operativo/partials/desarrollo.html', {'notas': notas})


def guardar_todo(request):
    if request.method == "POST":
        data = json.loads(request.body)
        notas = data.get('notas', [])
        for n in notas:
            Nota.objects.create(apartado=n['apartado'], texto=n['texto'])
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


def historial_notas(request):
    notas = Nota.objects.all().order_by('-fecha_creacion')
    return render(request, 'modulo/historial_notas.html', {'notas': notas})


def crear_acuerdo_operativo(request):
    integrantes = Integrante.objects.all().order_by('area__nombre', 'nombre_completo')
    unidades = list(range(1, 10))

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
    acuerdos = AcuerdoOperativo.objects.all().order_by('-fecha_creacion')
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
        seleccionados_ids = request.POST.getlist("integrantes")
        request.session["integrantes_seleccionados"] = [str(i) for i in seleccionados_ids]
        return redirect("descarga")

    seleccionados_ids = request.session.get("integrantes_seleccionados", [])
    seleccionados = Integrante.objects.filter(id__in=seleccionados_ids)

    return render(request, "modulo/integrantes.html", {
        "integrantes": integrantes,
        "seleccionados": seleccionados,
    })


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


def descargar_pdf(request):
    if request.method == "POST":
        # Obtener IDs seleccionados desde el formulario
        notas_ids = request.POST.getlist("notas_seleccionadas")
        acuerdos_ids = request.POST.getlist("acuerdos_seleccionados")
        integrantes_ids = request.POST.getlist("integrantes")  # agregar en tu form hidden inputs si es necesario

        # Consultar objetos en la base de datos
        integrantes = Integrante.objects.filter(id__in=integrantes_ids)
        notas = Nota.objects.filter(id__in=notas_ids)
        acuerdos = AcuerdoOperativo.objects.filter(id__in=acuerdos_ids)

        # Preparar los textos para la plantilla
        fecha = date.today().strftime("%d/%m/%Y")
        txt_integrantes = "\n".join([f"{i+1}. {x.nombre_completo} - {x.puesto}" for i, x in enumerate(integrantes)])
        txt_notas = "\n".join([f"{i+1}. {x.get_apartado_display()} - {x.texto}" for i, x in enumerate(notas)])
        txt_acuerdos = "\n".join([f"{i+1}. {x.numerador}. {x.acuerdo} ({x.responsable.nombre_completo})" for i, x in enumerate(acuerdos)])

        # Contexto para la plantilla
        context = {
            "FECHA": fecha,
            "INTEGRANTES": txt_integrantes,
            "NOTAS": txt_notas,
            "ACUERDOS": txt_acuerdos,
        }

        # Renderizar HTML desde imprimir.html
        html_string = render_to_string("modulo/imprimir.html", context)

        # Generar PDF
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="Minuta_Reunion.pdf"'

        pisa_status = pisa.CreatePDF(io.BytesIO(html_string.encode("UTF-8")), dest=response)

        if pisa_status.err:
            return HttpResponse(f"Error al generar el PDF <pre>{html_string}</pre>")

        return response

    return HttpResponse("Método no permitido", status=405)
