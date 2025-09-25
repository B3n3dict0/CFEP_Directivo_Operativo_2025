# operativo/models.py
from django.db import models

class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Integrante(models.Model):
    nombre_completo = models.CharField(max_length=200)
    puesto = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="integrantes")

    def __str__(self):
        return f"{self.nombre_completo} - {self.puesto}"


#aqui empieza mi logica para crear acuerdos operativo
class AcuerdoOperativo(models.Model):
    numerador = models.PositiveIntegerField()
    unidad = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 10)])
    acuerdo = models.TextField()
    unidad_parada = models.BooleanField(default=False)
    fecha_limite = models.DateField()
    pendiente = models.BooleanField(default=True)
    responsable = models.ForeignKey('Integrante', on_delete=models.CASCADE, related_name="acuerdos")
    porcentaje_avance = models.PositiveSmallIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.numerador} - {self.acuerdo[:30]}"