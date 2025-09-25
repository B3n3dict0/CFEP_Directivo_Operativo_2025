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
