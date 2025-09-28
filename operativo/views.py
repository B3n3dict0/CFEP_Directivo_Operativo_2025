from django.utils import timezone
from directivo import models
from .forms import IntegranteForm
from .models import AcuerdoOperativo, Integrante
import os
from django.conf import settings
from django.http import HttpResponse
from docx import Document
from docx2pdf import convert
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from .models import Nota
from .forms import NotaForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

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
    
    
# Logica para descargar pdf
def exportar_pdf(request):
    if request.method == "POST" and "descargar_pdf" in request.POST:
        # 📌 Datos dinámicos
        fecha = timezone.now().strftime("%Y-%m-%d")
        integrantes = request.POST.getlist("integrantes")
        notas = request.POST.get("notas", "")
        acuerdos = request.POST.getlist("acuerdo")

        # 📌 Abrir plantilla Word
        plantilla_path = os.path.join(settings.BASE_DIR, "operativo/templates/plantillas/Operativa.docx")
        doc = Document(plantilla_path)

        # 👉 Aquí deberías buscar los marcadores y reemplazarlos
        for p in doc.paragraphs:
            if "{{ fecha }}" in p.text:
                p.text = p.text.replace("{{ fecha }}", fecha)
            if "{{ notas }}" in p.text:
                p.text = p.text.replace("{{ notas }}", notas)

        # 👉 Insertar integrantes
        for p in doc.paragraphs:
            if "{{ integrantes }}" in p.text:
                p.text = p.text.replace("{{ integrantes }}", "")
                for i in integrantes:
                    doc.add_paragraph(f"- {i}", style="List Bullet")

        # 👉 Insertar acuerdos
        for p in doc.paragraphs:
            if "{{ acuerdos }}" in p.text:
                p.text = p.text.replace("{{ acuerdos }}", "")
                for ac in acuerdos:
                    doc.add_paragraph(f"• {ac}", style="List Bullet")

        # 📌 Ruta de almacenamiento interno (copias del proyecto)
        carpeta_base = os.path.join(settings.BASE_DIR, "operativo", "documentos", fecha)
        os.makedirs(carpeta_base, exist_ok=True)

        # Guardar Word en carpeta del proyecto
        word_path = os.path.join(carpeta_base, f"Acta_{fecha}.docx")
        doc.save(word_path)

        # 📌 Convertir Word a PDF temporalmente
        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        convert(word_path, tmp_pdf.name)

        # 📌 Devolver PDF al navegador
        with open(tmp_pdf.name, "rb") as f:
            pdf_data = f.read()
        os.unlink(tmp_pdf.name)  # limpiar temporal

        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="Acta_{fecha}.pdf"'
        return response

    return HttpResponse("No se enviaron datos.")