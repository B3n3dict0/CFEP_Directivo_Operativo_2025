from django.urls import path
from . import views

urlpatterns = [
    # Dashboard administrador
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # CRUD tareas
    path('', views.tasks, name='tasks'),
    path('completed/', views.tasks_completed, name='tasks_completed'),
    path('create/', views.create_task, name='create_task'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('<int:task_id>/delete/', views.delete_task, name='delete_task'),

    # 🧹 Panel de eliminación para superusuario
    path('eliminar_directivo/', views.eliminar_directivo_panel, name='eliminar_directivo'),
    path('eliminar_directivo/nota/<int:nota_id>/', views.eliminar_nota_directivo, name='eliminar_nota_directivo'),
    path('eliminar_directivo/acuerdo/<int:acuerdo_id>/', views.eliminar_acuerdo_directivo, name='eliminar_acuerdo_directivo'),
]
