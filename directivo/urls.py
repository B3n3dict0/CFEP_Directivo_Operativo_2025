from django.urls import path
from . import views

urlpatterns = [
    # Vista principal del módulo Directiva
    path('', views.directivo_view, name='directivo_index'),

    # Acuerdos Directiva
    path('crear-acuerdo/', views.crear_acuerdo_directivo, name='directivo_crear_acuerdo'),
    path('historial-acuerdos/', views.historial_acuerdos, name='directivo_historial_acuerdos'),
    path("editar/<int:id>/", views.editar_acuerdo_directivo, name="editar_acuerdo_directivo"),

    # Notas Directiva
    path('descarga/', views.descarga_directiva, name='descarga_directiva'),
    path('editar-nota/<int:nota_id>/', views.editar_nota_directivo, name='directivo_editar_nota'),
    path('guardar-todo/', views.guardar_todo_directivo, name='directivo_guardar_todo'),
    path('descargar_word_directiva/', views.descargar_word_directiva, name='descargar_word_directiva'),
    
]
