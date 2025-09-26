from django.urls import path
from . import views

urlpatterns = [
    path('', views.directivo_view, name='directivo_index'),
    path('crear-acuerdo/', views.crear_acuerdo_directivo, name='crear_acuerdo_directivo'),
    path('historial-acuerdos/', views.historial_acuerdos, name='historial_acuerdos'),
    path('exportar-pdf/', views.exportar_pdf, name='exportar_pdf'),

    # Notas
    path('editar/<int:nota_id>/', views.editar_nota, name='editar_nota'),
    path('guardar-todo/', views.guardar_todo, name='guardar_todo'),
]
