import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangocrud.settings')
django.setup()


from operativo.models import Area, Integrante

# Áreas
areas = [
    "SUPERINTENDENTE GENERAL",
    "SUPERINTENDENTE DE PRODUCCIÓN",
    "SUPERINTENDENTE DE MANTENIMIENTO",
    "JEFES DE DEPARTAMENTOS",
    "ADMINISTRADOR",
    "SUPERVISORES",
    "SUPERINTENDENTE DE TURNO",
    "JEFES OFICINA",
]

for nombre_area in areas:
    Area.objects.get_or_create(nombre=nombre_area)

# Integrantes
integrantes = [
    ("Ing. Sergio Rafael Gonzalez López", "Superintendente General E.F.", "SUPERINTENDENTE GENERAL"),
    ("Ing. Carlos Manuel Gutierrez Cardozo", "Superintendente de Producción E.F.", "SUPERINTENDENTE DE PRODUCCIÓN"),
    ("Ing. Héctor Javier Durán Novelo", "Superintendente de Mantenimiento E.F.", "SUPERINTENDENTE DE MANTENIMIENTO"),
    ("Ing. Francisco Jose Lara Moreno", "Jefe Depto. Mecánico E.F.", "JEFES DE DEPARTAMENTOS"),
    ("Ing. Keith Andrés Carama Loría", "Jefe Depto. Eléctrico", "JEFES DE DEPARTAMENTOS"),
    ("Ing. Jose Ahmed Cazares Baeza", "Jefe Depto. Instrumentación y Control", "JEFES DE DEPARTAMENTOS"),
    ("Lic. Henry Manuel Mendez Contreras", "Jefe Depto. Programación y Control E.F.", "ADMINISTRADOR"),
    ("Ing. Reynaldo Ordaz Santiago", "Supervisor Civil", "SUPERVISORES"),
    ("Ing. Suemy Reyes García", "Jefe Depto. Químico", "JEFES DE DEPARTAMENTOS"),
    ("Joaquín Gustavo Valerio Flores", "Jefe Depto. Capacitación y Seguridad E.F.", "JEFES DE DEPARTAMENTOS"),
    ("Nelly del Carmen Martínez Perez", "Supervisor Ambiental E.F.", "JEFES DE DEPARTAMENTOS"),
    ("Arq. Elías Delgadillo Vallejo", "Supervisor Civil", "SUPERVISORES"),
    ("Ing. Héctor Alejandro Ramos Perez", "Supervisor de Operación E.F.", "SUPERINTENDENTE DE TURNO"),
    ("Lic. Alexis Cruz Novelo", "Depto. de Programación y Control", "JEFES OFICINA"),
    ("Juan Trinidad Osorno Carrillo", "Supervisor Eléctrico E.F.", "SUPERVISORES"),
    ("Gilberto Adrián Moo Coral", "Supervisor Eléctrico E.F.", "SUPERVISORES"),
    ("Sergio Uscanga Morales", "Supervisor de Instrumentación y Control E.F.", "SUPERVISORES"),
    ("Jesus Antonio Aguilar Carrillo", "Supervisor de Instrumentación y Control E.F.", "SUPERVISORES"),
]

for nombre, puesto, nombre_area in integrantes:
    area = Area.objects.get(nombre=nombre_area)
    Integrante.objects.get_or_create(
        nombre_completo=nombre,
        puesto=puesto,
        area=area
    )

print("Integrantes insertados correctamente ✅")
