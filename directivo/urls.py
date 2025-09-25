# urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    # Acuerdos directivo
    path('', views.directivo_view, name='directivo_index'),  # para /usuarios/directivo/

]
