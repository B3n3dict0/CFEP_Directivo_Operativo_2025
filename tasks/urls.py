from django.urls import path
from . import views

urlpatterns = [
    # Dashboard administrador
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # CRUD tareas
    path('usuarios/gestionar/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('usuarios/editar/<int:user_id>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # 🧹 Panel de eliminación para superusuario Directivo
    path('eliminar_directivo/', views.eliminar_directivo_panel, name='eliminar_directivo'),
    path('eliminar_directivo/nota/<int:nota_id>/', views.eliminar_nota_directivo, name='eliminar_nota_directivo'),
    path('eliminar_directivo/acuerdo/<int:acuerdo_id>/', views.eliminar_acuerdo_directivo, name='eliminar_acuerdo_directivo'),

    # 🧹 Panel de eliminación para Operativo
    path('eliminar_operativo/', views.eliminar_operativo_panel, name='eliminar_operativo_panel'),
    path('eliminar_operativo/integrante/<int:integrante_id>/', views.eliminar_integrante, name='eliminar_integrante'),
    path('eliminar_operativo/nota/<int:nota_id>/', views.eliminar_nota, name='eliminar_nota'),
    path('eliminar_operativo/acuerdo/<int:acuerdo_id>/', views.eliminar_acuerdo, name='eliminar_acuerdo'),
    
    # panel de directivo del word respaldo
    path("word/", views.listar_word, name="listar_word"),
    path("word/descargar/<str:nombre_archivo>/", views.descargar_word, name="descargar_word"),
    path("word/eliminar/<path:nombre_archivo>/", views.eliminar_word, name="eliminar_word"),
    
    # panel de operativo del word respaldo
    path('operativo/word/', views.listar_word_operativo, name='listar_word_operativo'),
    path('operativo/word/descargar/<str:nombre_archivo>/', views.descargar_word_operativo, name='descargar_word_operativo'),
    path('operativo/word/eliminar/<str:nombre_archivo>/', views.eliminar_word_operativo, name='eliminar_word_operativo'),


]
