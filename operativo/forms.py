# operativo/forms.py
from django import forms
from .models import Integrante, Area
from .models import Nota

class IntegranteForm(forms.ModelForm):
    class Meta:
        model = Integrante
        fields = ['nombre_completo', 'puesto', 'area']

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre']

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['apartado', 'texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }