from django.urls import path
from . import views

urlpatterns = [
    path('', views.operativo_view, name='operativo_index'),
    path('crear-acuerdo/', views.crear_acuerdo_operativo, name='crear_acuerdo_operativo'),

]
