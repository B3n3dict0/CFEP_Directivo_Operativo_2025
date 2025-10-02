# Python estándar
import os
import io
import json
import tempfile
from datetime import date

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
from directivo import models
from directivo.models import NotaDirectivo, AcuerdoDirectivo, Integrante, Nota
from operativo.models import Integrante  # modelo compartido

# Formularios
from directivo.forms import NotaDirectivoForm, IntegranteForm
from operativo.forms import NotaForm, IntegranteForm  # IntegranteForm repetido, revisar si se usa operativo o directivo

# Para exportar Word a PDF
from docx import Document
from docx2pdf import convert
from django.shortcuts import render, get_object_or_404, redirect
from .models import NotaDirectivo
from .forms import NotaDirectivoForm


# View principal de directivo
def directivo_view(request):
    # Formulario para agregar integrantes
    if request.method == "POST" and 'agregar_integrante' in request.POST:
        form = IntegranteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('directivo_index')
    else:
        form = IntegranteForm()

    # Traer todos los integrantes existentes
    integrantes = Integrante.objects.all().order_by('area__nombre', 'nombre_completo')

    # Búsqueda opcional
    query = request.GET.get('q')
    if query:
        integrantes = integrantes.filter(nombre_completo__icontains=query)

    seleccionados = []  # Solo JS maneja seleccionados temporalmente

    return render(request, "directivo/base.html", {
        'integrantes': integrantes,
        'form': form,
        'seleccionados': seleccionados,
        'fecha_actual': timezone.now(),
    })

# Notas
def lista_notas(request):
    notas = Nota.objects.all().order_by('-fecha_creacion')
    return render(request, 'directivo/partials/desarrollo.html', {'notas': notas})

def editar_nota_directivo(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    if request.method == "POST":
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            return redirect('directivo_index')
    else:
        form = NotaForm(instance=nota)
    return render(request, 'directivo/partials/desarrollo.html', {'form': form, 'nota': nota})

@csrf_exempt
def guardar_todo_directivo(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            notas = data.get("notas", [])
            for n in notas:
                if n["texto"].strip():
                    NotaDirectivo.objects.create(apartado=n["apartado"], texto=n["texto"])
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "msg": str(e)}, status=400)
    return JsonResponse({"status": "error"}, status=400)


# Crear acuerdo directivo
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

# Historial de acuerdos
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





# --- Vista para mostrar formulario y selección ---
def descarga_directiva(request):
    integrantes = Integrante.objects.all().order_by("area__nombre", "nombre_completo")
    notas = NotaDirectivo.objects.all().order_by("fecha_creacion")
    acuerdos = AcuerdoDirectivo.objects.all().order_by("fecha_creacion")
    form = IntegranteForm()

    return render(request, "modulo/descarga_directivo.html", {
        "integrantes": integrantes,
        "seleccionados": [],
        "notas": notas,
        "acuerdos": acuerdos,
        "form": form
    })

# --- Función para buscar imágenes en STATICFILES_DIRS ---
def buscar_imagen(nombre_archivo):
    for carpeta in settings.STATICFILES_DIRS:
        ruta = os.path.join(carpeta, "img", nombre_archivo)
        if os.path.exists(ruta):
            return ruta
    return None

# --- Encabezado y pie de página PDF ---
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

    # Pie de página
    canvas.setStrokeColor(colors.grey)
    canvas.line(1*cm, 2*cm, 20*cm, 2*cm)
    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(20*cm, 1.2*cm, f"Página {page_num}")

# --- Vista para generar PDF ---
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

        # --- Título principal ---
        titulo = [[Paragraph('<font color="white"><b>MINUTA DE REUNIÓN DIRECTIVA</b></font>', normal)]]
        tabla_titulo = Table(titulo, colWidths=[doc.width])
        tabla_titulo.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.darkblue),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("FONTSIZE", (0,0), (-1,-1), 14),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6),
        ]))
        elementos.append(tabla_titulo)
        elementos.append(Spacer(1, 12))

        # --- Datos Generales ---
        datos_generales = [
            [Paragraph("MINUTA DE REUNIÓN DIRECTIVA", normal), Paragraph("Reunión Directiva Central Felipe Carrillo Puerto", normal)],
            [Paragraph("Lugar:", normal), Paragraph("Sala de Juntas Directiva", normal), Paragraph("Fecha y Horario:", normal), Paragraph(fecha, normal)],
        ]
        tabla_datos = Table(datos_generales, colWidths=[doc.width*0.25, doc.width*0.35, doc.width*0.2, doc.width*0.2])
        tabla_datos.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        elementos.append(tabla_datos)
        elementos.append(Spacer(1, 12))

        # --- Objetivo, Importancia y Participantes ---
        tabla_objetivo_importancia = [
            [Paragraph("<b>Objetivo(s)</b>", normal)],
            [Paragraph("PROPÓSITO: Revisión de decisiones estratégicas, seguimiento a acuerdos directivos y control administrativo.", normal)],
            [Paragraph("IMPORTANCIA: Asegurar la toma de decisiones correcta, cumplir metas institucionales y seguimiento de proyectos clave.", normal)],
            [Paragraph("<b>Participantes</b>", normal)],
            [Paragraph(", ".join([f"{i}. {x.nombre_completo} - {x.puesto}" for i, x in enumerate(integrantes, start=1)]), normal)],
        ]
        tabla_obj_imp = Table(tabla_objetivo_importancia, colWidths=[doc.width])
        tabla_obj_imp.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        elementos.append(tabla_obj_imp)
        elementos.append(Spacer(1, 12))

        # --- Desarrollo ---
        desarrollo_list = [[Paragraph(f"{i}. {x.get_apartado_display()} - {x.texto}", normal)] for i, x in enumerate(notas, start=1)]
        tabla_desarrollo = Table([[Paragraph("<b>Desarrollo</b>", normal)]] + desarrollo_list, colWidths=[doc.width])
        tabla_desarrollo.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ]))
        elementos.append(tabla_desarrollo)
        elementos.append(Spacer(1, 12))

        # --- Acuerdos ---
        acuerdos_list = [[Paragraph(f"{i}. {x.numerador}. {x.acuerdo} ({x.responsable.nombre_completo})", normal)] for i, x in enumerate(acuerdos, start=1)]
        tabla_acuerdos = Table([[Paragraph("<b>Compromisos y Acuerdos</b>", normal)]] + acuerdos_list, colWidths=[doc.width])
        tabla_acuerdos.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ]))
        elementos.append(tabla_acuerdos)
        elementos.append(Spacer(1, 12))

        # --- Generar PDF ---
        doc.build(elementos, onFirstPage=encabezado_y_pie, onLaterPages=encabezado_y_pie)

        pdf = buffer.getvalue()
        buffer.close()
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="Minuta_Reunion_Directiva.pdf"'
        response.write(pdf)
        return response

    return HttpResponse("Método no permitido", status=405)

