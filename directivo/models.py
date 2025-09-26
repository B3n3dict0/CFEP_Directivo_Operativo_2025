from django.db import models
from django.utils import timezone

# Importar modelos compartidos desde operativo
from operativo.models import Area, Integrante, Nota


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
