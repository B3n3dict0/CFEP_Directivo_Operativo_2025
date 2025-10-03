# Python estándar
import io
from datetime import date
import os
import json

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# Modelos
from .models import NotaDirectivo, AcuerdoDirectivo, Integrante

# Formularios
from .forms import NotaDirectivoForm, IntegranteForm
from directivo import models


# ---------------- VIEWS ----------------

def directivo_view(request):
    # Agregar integrante
    if request.method == "POST" and 'agregar_integrante' in request.POST:
        form = IntegranteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('directivo_index')
    else:
        form = IntegranteForm()

    integrantes = Integrante.objects.all().order_by('area__nombre', 'nombre_completo')

    # Búsqueda
    query = request.GET.get('q')
    if query:
        integrantes = integrantes.filter(nombre_completo__icontains=query)

    # Integrantes seleccionados en session
    seleccionados_ids = request.session.get("integrantes_seleccionados", [])
    seleccionados = Integrante.objects.filter(id__in=seleccionados_ids)

    return render(request, "directivo/base.html", {
        'integrantes': integrantes,
        'form': form,
        'seleccionados': seleccionados,
        'fecha_actual': timezone.now(),
    })


def lista_notas_directivo(request):
    notas = NotaDirectivo.objects.all().order_by('-fecha_creacion')
    return render(request, 'directivo/partials/desarrollo.html', {'notas': notas})


def editar_nota_directivo(request, nota_id):
    nota = get_object_or_404(NotaDirectivo, id=nota_id)
    if request.method == "POST":
        form = NotaDirectivoForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            return redirect('directivo_index')
    else:
        form = NotaDirectivoForm(instance=nota)
    return render(request, 'directivo/partials/editar_nota.html', {'form': form, 'nota': nota})


@csrf_exempt
def guardar_todo_directivo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            notas = data.get("notas", [])
            for n in notas:
                # Guardar solo si tiene texto
                if n.get("texto", "").strip():
                    NotaDirectivo.objects.create(apartado=n["apartado"], texto=n["texto"])
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "msg": str(e)}, status=400)
    return JsonResponse({"status": "error"}, status=400)


# ---------------- REGLAS ----------------

def crear_acuerdo_directivo(request):
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
            AcuerdoDirectivo.objects.create(
                numerador=int(filas[i]),
                unidad=int(unidades_post[i]),
                acuerdo=acuerdos[i],
                unidad_parada=(unidad_paradas[i] == 'on') if i < len(unidad_paradas) else False,
                fecha_limite=fechas_limite[i],
                pendiente=(pendientes[i] == 'on') if i < len(pendientes) else True,
                responsable_id=int(responsables[i]),
                porcentaje_avance=int(avances[i])
            )
        return redirect('crear_acuerdo_directivo')

    return render(request, 'modulo/crear_acuerdo_directivo.html', {
        'integrantes': integrantes,
        'fecha_actual': timezone.now(),
        'unidades': unidades
    })


def historial_acuerdos(request):
    acuerdos = AcuerdoDirectivo.objects.all().order_by('-fecha_creacion')
    query = request.GET.get('q')
    if query:
        acuerdos = acuerdos.filter(
            models.Q(acuerdo__icontains=query) |
            models.Q(numerador__icontains=query) |
            models.Q(responsable__nombre_completo__icontains=query)
        )
    return render(request, 'modulo/historial_acuerdo_directivo.html', {
        'acuerdos': acuerdos,
        'query': query,
    })


# ---------------- Selección y Descarga ----------------

def seleccionar_integrantes_directivo(request):
    integrantes = Integrante.objects.all().order_by("area__nombre", "nombre_completo")

    if request.method == "POST":
        seleccionados_ids = request.POST.getlist("integrantes")
        request.session["integrantes_seleccionados"] = [str(i) for i in seleccionados_ids]
        return redirect("descarga_directiva")

    seleccionados_ids = request.session.get("integrantes_seleccionados", [])
    seleccionados = Integrante.objects.filter(id__in=seleccionados_ids)

    return render(request, "modulo/integrantes_directivo.html", {
        "integrantes": integrantes,
        "seleccionados": seleccionados,
    })


def descarga_directiva(request):
    integrantes = Integrante.objects.all().order_by("area__nombre", "nombre_completo")
    notas = NotaDirectivo.objects.all().order_by('-fecha_creacion')
    acuerdos = AcuerdoDirectivo.objects.all().order_by('-fecha_creacion')
    seleccionados_ids = request.session.get("integrantes_seleccionados", [])
    seleccionados = Integrante.objects.filter(id__in=seleccionados_ids)
    form = IntegranteForm()

    return render(request, "modulo/descarga_directivo.html", {
        "integrantes": integrantes,
        "seleccionados": seleccionados,
        "notas": notas,
        "acuerdos": acuerdos,
        "form": form
    })


# ---------------- Funciones PDF ----------------

def buscar_imagen(nombre_archivo):
    for carpeta in settings.STATICFILES_DIRS:
        ruta = os.path.join(carpeta, "img", nombre_archivo)
        if os.path.exists(ruta):
            return ruta
    return None


def encabezado_y_pie(canvas, doc):
    encabezado = buscar_imagen("encabezado.jpg")
    if encabezado:
        img = ImageReader(encabezado)
        ancho_original, alto_original = img.getSize()
        ancho_pdf = A4[0] - 2*cm
        escala = ancho_pdf / ancho_original
        alto_final = alto_original * escala

        canvas.drawImage(
            encabezado,
            1*cm,
            A4[1] - alto_final - 1*cm,
            width=ancho_pdf,
            height=alto_final,
            preserveAspectRatio=True,
            mask='auto'
        )

    canvas.setStrokeColor(colors.grey)
    canvas.line(1*cm, 2*cm, 20*cm, 2*cm)
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(20*cm, 1.2*cm, f"Página {page_num}")


def descargar_pdf_directiva(request):
    if request.method == "POST":
        notas_ids = request.POST.getlist("notas_seleccionadas")
        acuerdos_ids = request.POST.getlist("acuerdos_seleccionados")
        integrantes_ids = request.POST.getlist("integrantes")

        integrantes = Integrante.objects.filter(id__in=integrantes_ids)
        notas = NotaDirectivo.objects.filter(id__in=notas_ids)
        acuerdos = AcuerdoDirectivo.objects.filter(id__in=acuerdos_ids)

        fecha = date.today().strftime("%d/%m/%Y")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=5*cm, bottomMargin=3*cm)

        elementos = []
        styles = getSampleStyleSheet()
        normal = styles["Normal"]
        normal.fontSize = 10

        heading = styles["Heading3"]
        heading.fontSize = 12

        # Aquí va tu lógica de tablas PDF igual que antes
        doc.build(elementos, onFirstPage=encabezado_y_pie, onLaterPages=encabezado_y_pie)

        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="Minuta_Reunion_Directiva.pdf"'
        response.write(pdf)
        return response

    return HttpResponse("Método no permitido", status=405)
