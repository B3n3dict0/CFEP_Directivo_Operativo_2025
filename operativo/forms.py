# operativo/forms.py
from django import forms
from .models import Integrante, Area

class IntegranteForm(forms.ModelForm):
    class Meta:
        model = Integrante
        fields = ['nombre_completo', 'puesto', 'area']

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre']
