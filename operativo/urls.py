from django.urls import path
from . import views

urlpatterns = [
    path('', views.operativo_view, name='operativo_index'),
    path('crear-acuerdo/', views.crear_acuerdo_operativo, name='crear_acuerdo_operativo'),
    path('historial-acuerdo_operativo/', views.historial_acuerdo_operativo, name='historial_acuerdo_operativo'),
    path('editar/<int:acuerdo_id>/', views.editar_acuerdo_operativo, name='editar_acuerdo_operativo'),
    path('eliminar/<int:acuerdo_id>/', views.eliminar_acuerdo_operativo, name='eliminar_acuerdo_operativo'),
   
    # Rutas nuevas para notas
    path('editar/<int:nota_id>/', views.editar_nota, name='editar_nota'),
    path('guardar-todo/', views.guardar_todo, name='guardar_todo'),
    path('descarga/', views.descarga, name='descarga'),
    path('descargar-pdf/', views.descargar_pdf, name='descargar_pdf'),
]
