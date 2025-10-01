from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import os, tempfile, json

from docx import Document
from docx2pdf import convert

# Importar modelos y formularios
from operativo.models import Integrante, Nota  # Compartidos
from .models import AcuerdoDirectivo
from .forms import IntegranteForm, NotaForm
from directivo import models

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

def editar_nota(request, nota_id):
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
def guardar_todo(request):
    if request.method == "POST":
        data = json.loads(request.body)
        notas = data.get('notas', [])
        for n in notas:
            Nota.objects.create(apartado=n['apartado'], texto=n['texto'])
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

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

# Exportar PDF
def exportar_pdf(request):
    if request.method == "POST" and "descargar_pdf" in request.POST:
        fecha = timezone.now().strftime("%Y-%m-%d")
        integrantes = request.POST.getlist("integrantes")
        notas = request.POST.get("notas", "")
        acuerdos = request.POST.getlist("acuerdo")

        plantilla_path = os.path.join(settings.BASE_DIR, "directivo/templates/plantillas/Directiva.docx")
        doc = Document(plantilla_path)

        for p in doc.paragraphs:
            if "{{ fecha }}" in p.text:
                p.text = p.text.replace("{{ fecha }}", fecha)
            if "{{ notas }}" in p.text:
                p.text = p.text.replace("{{ notas }}", notas)
            if "{{ integrantes }}" in p.text:
                p.text = p.text.replace("{{ integrantes }}", "")
                for i in integrantes:
                    doc.add_paragraph(f"- {i}", style="List Bullet")
            if "{{ acuerdos }}" in p.text:
                p.text = p.text.replace("{{ acuerdos }}", "")
                for ac in acuerdos:
                    doc.add_paragraph(f"• {ac}", style="List Bullet")

        carpeta_base = os.path.join(settings.BASE_DIR, "directivo", "documentos", fecha)
        os.makedirs(carpeta_base, exist_ok=True)
        word_path = os.path.join(carpeta_base, f"Acta_{fecha}.docx")
        doc.save(word_path)

        tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        convert(word_path, tmp_pdf.name)

        with open(tmp_pdf.name, "rb") as f:
            pdf_data = f.read()
        os.unlink(tmp_pdf.name)

        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="Acta_{fecha}.pdf"'
        return response

    return HttpResponse("No se enviaron datos.")
