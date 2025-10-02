from django.db import models
from django.utils import timezone

# Importar modelos compartidos desde operativo
from operativo.models import Area, Integrante, Nota
from django.db import models

class NotaDirectivo(models.Model):
    APARTADOS = [
        ('produccion', 'Producción'),
        ('mantenimiento', 'Mantenimiento'),
        ('gestion', 'Gestión de Recursos'),
        ('seguridad', 'Seguridad, Ambiental y Calidad'),
        ('superintendencia', 'Superintendencia General'),
    ]

    apartado = models.CharField(max_length=50, choices=APARTADOS)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_apartado_display()} - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"


# Modelo específico para acuerdos directivo
class AcuerdoDirectivo(models.Model):
    numerador = models.PositiveIntegerField()
    unidad = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 10)])
    acuerdo = models.TextField()
    unidad_parada = models.BooleanField(default=False)
    fecha_limite = models.DateField()
    pendiente = models.BooleanField(default=True)
    responsable = models.ForeignKey(Integrante, on_delete=models.CASCADE, related_name="acuerdos_directivo")
    porcentaje_avance = models.PositiveSmallIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.numerador} - {self.acuerdo[:30]}"
