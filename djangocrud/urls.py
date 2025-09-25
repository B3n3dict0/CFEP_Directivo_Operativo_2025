"""djangocrud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tasks import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.signout, name='logout'),
    path('signup/', views.signup, name='signup'),  # si quieres que solo admin cree usuarios, lo puedes proteger en la vista
    path('admin/', admin.site.urls),

    # Todas las rutas de tareas (CRUD)
    path('tasks/', include('tasks.urls')),

    # Menú de usuarios
    path('usuarios/', include('usuarios.urls')),  
]
