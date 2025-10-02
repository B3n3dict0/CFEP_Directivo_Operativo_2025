from django import forms
# Importar los modelos compartidos desde operativo
from operativo.models import Integrante, Area
# Importar los modelos específicos de directivo
from .models import NotaDirectivo

class IntegranteForm(forms.ModelForm):
    class Meta:
        model = Integrante
        fields = ['nombre_completo', 'puesto', 'area']

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre']

class NotaDirectivoForm(forms.ModelForm):
    class Meta:
        model = NotaDirectivo
        fields = ['apartado', 'texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu nota aquí...'}),
            'apartado': forms.HiddenInput()
        }
