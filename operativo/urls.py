from django.urls import path
from . import views

urlpatterns = [
    path('', views.operativo_view, name='operativo_index'),
    path('crear-acuerdo/', views.crear_acuerdo_operativo, name='crear_acuerdo_operativo'),
    path('historial-acuerdo_operativo/', views.historial_acuerdo_operativo, name='historial_acuerdo_operativo'),
    path('exportar-pdf/', views.exportar_pdf, name='exportar_pdf'),
    
    # Rutas nuevas para notas
    path('editar/<int:nota_id>/', views.editar_nota, name='editar_nota'),
    path('guardar-todo/', views.guardar_todo, name='guardar_todo'),
    path('historial-notas/', views.historial_notas, name='historial_notas'),

]
