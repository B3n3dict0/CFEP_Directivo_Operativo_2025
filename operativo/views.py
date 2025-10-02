from datetime import date
import json
import io
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from operativo import models
from djangocrud import settings
from .forms import IntegranteForm, NotaForm
from .models import AcuerdoOperativo, Integrante, Nota
import io
from datetime import date
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from .models import Integrante, Nota, AcuerdoOperativo 
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph


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










# --- Función para buscar imágenes en STATICFILES_DIRS ---
def buscar_imagen(nombre_archivo):
    for carpeta in settings.STATICFILES_DIRS:
        ruta = os.path.join(carpeta, "img", nombre_archivo)
        if os.path.exists(ruta):
            return ruta
    return None  # Devuelve None si no se encuentra




def encabezado_y_pie(canvas, doc):
    # Ruta de tu imagen de encabezado
    encabezado = buscar_imagen("encabezado.jpg")  # tu imagen combinada

    if encabezado:
        img = ImageReader(encabezado)
        ancho_original, alto_original = img.getSize()
        ancho_pdf = A4[0] - 2*cm  # ancho total menos márgenes
        escala = ancho_pdf / ancho_original
        alto_final = alto_original * escala

        # Dibujar la imagen en la parte superior
        canvas.drawImage(
            encabezado,
            1*cm,            # margen izquierdo
            A4[1] - alto_final - 1*cm,  # altura desde el borde superior
            width=ancho_pdf,
            height=alto_final,
            preserveAspectRatio=True,
            mask='auto'
        )

    # --- Pie de página ---
    canvas.setStrokeColor(colors.grey)
    canvas.line(1*cm, 2*cm, 20*cm, 2*cm)

    page_num = canvas.getPageNumber()
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(20*cm, 1.2*cm, f"Página {page_num}")

# --- Vista para generar PDF ---
def descargar_pdf(request):
    if request.method == "POST":
        # Obtener datos seleccionados
        notas_ids = request.POST.getlist("notas_seleccionadas")
        acuerdos_ids = request.POST.getlist("acuerdos_seleccionados")
        integrantes_ids = request.POST.getlist("integrantes")

        # Consultar BD
        integrantes = Integrante.objects.filter(id__in=integrantes_ids)
        notas = Nota.objects.filter(id__in=notas_ids)
        acuerdos = AcuerdoOperativo.objects.filter(id__in=acuerdos_ids)

        fecha = date.today().strftime("%d/%m/%Y")

        # --- Preparar contenido PDF ---
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
        titulo = [[Paragraph('<font color="white"><b>MINUTA DE REUNIÓN</b></font>', normal)]]
        tabla_titulo = Table(titulo, colWidths=[doc.width])
        tabla_titulo.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("FONTSIZE", (0,0), (-1,-1), 14),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6),
        ]))
        elementos.append(tabla_titulo)
        elementos.append(Spacer(1, 12))

        # --- Tabla 1: Datos Generales ---
        datos_generales = [
            [Paragraph("MINUTA DE REUNIÓN", normal), Paragraph("Reunión Operativa Central Felipe Carrillo Puerto", normal)],
            [Paragraph("Lugar:", normal), Paragraph("Sala de Juntas de la Central FCP", normal), Paragraph("Fecha y Horario:", normal), Paragraph(fecha, normal)],
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

        # --- Tabla 2: Objetivo, Importancia y Participantes ---
        tabla_objetivo_importancia = [
            [Paragraph("<b>Objetivo(s)</b>", normal)],
            [Paragraph("PROPÓSITO: Informar el estado de las unidades, proporcionar la problemática prioritaria de las áreas operativas e informar el avance de los programas de mantenimiento.", normal)],
            [Paragraph("IMPORTANCIA: Que el personal oriente sus actividades a la solución de las necesidades prioritarias para mantener las unidades operando en forma confiable y segura, además de informar el avance de los proyectos de mantenimiento.", normal)],
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

        # --- Tabla 3: Orden del Día ---
        orden_dia = [
            ["1. ESTADO DE LAS UNIDADES …\nSEGUIMIENTO A REGIMEN TERMICO …\nSeguimiento Operativo Anomalías FCP\nAvisos de operación y química\nManiobras de riesgo", "Producción"],
            ["2. Seguimiento de actividades que originaron salida …\nAvance del proyecto de mantenimiento\nAvisos de mantenimiento predictivo\nActividades de riesgo", "Mantenimiento"],
            ["3. Avisos de atención inmediata relacionados con aspectos de seguridad", "Seguridad"],
            ["4. Eventos que afecten condiciones de seguridad", "Seguridad"],
            ["5. Eventos que afecten condiciones ambientales", "Ambiental"],
            ["6. Presentación de problemática y solución en materia de seguridad", "Seguridad"],
            ["7. Presentación de problemática y solución en materia ambiental", "Ambiental"],
            ["8. Revisión de Acuerdos Anteriores\nSeguimiento Operativo Anomalías FCP", "Calidad"],
            ["9. Creación de Acuerdos Nuevos\nSeguimiento Operativo Anomalías Central FCP", "Todos"],
            ["10. Ratificación de Actividades Prioritarias del Día", "Superintendencia General"],
        ]
        tabla_orden = Table(orden_dia, colWidths=[doc.width*0.7, doc.width*0.3])
        tabla_orden.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ]))
        elementos.append(tabla_orden)
        elementos.append(Spacer(1, 12))

        # --- Tabla 4: Desarrollo ---
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

        # --- Tabla 5: Compromisos y Acuerdos ---
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
        response["Content-Disposition"] = 'attachment; filename="Minuta_Reunion.pdf"'
        response.write(pdf)
        return response

    return HttpResponse("Método no permitido", status=405)

