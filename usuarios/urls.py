from django.urls import path, include
from . import views

urlpatterns = [
    path('menu/', views.menu_usuario, name='menu_usuario'),

    path('operativo/', include('operativo.urls')),   # Incluye operativo
    path('directivo/', include('directivo.urls')),   # Incluye directivo
]