from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from directivo.models import AcuerdoDirectivo, NotaDirectivo
from operativo.models import AcuerdoOperativo, Integrante, Nota
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages


# Create your views here.
# Solo superusuarios o staff pueden acceder
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm})
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"])
                user.save()
                return redirect('admin_dashboard')  # Redirige a donde quieras después de crear el usuario
            except IntegrityError:
                return render(
                    request,
                    'signup.html',
                    {"form": UserCreationForm, "error": "Username already exists."}
                )
        else:
            return render(
                request,
                'signup.html',
                {"form": UserCreationForm, "error": "Passwords did not match."}
            )


def home(request):
    return render(request, 'home.html')


@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    
    user = authenticate(
        request, username=request.POST['username'], password=request.POST['password']
    )
    
    if user is None:
        return render(request, 'signin.html', {
            "form": AuthenticationForm, 
            "error": "Usuario o contraseña incorrectos."
        })

    login(request, user)

    # Admin → dashboard en tasks/base.html
    if user.is_superuser or user.is_staff:
        return redirect('admin_dashboard')

    # Usuario normal → menú principal
    return redirect('menu_usuario')

@login_required
def admin_dashboard(request):
    return render(request, 'base.html')

# menu usuario
@login_required
def menu_usuario(request):
    return render(request, 'usuarios/menu.html')

    
    
    
# ------------------------------------------ directivo --------------------------------------------------------------    
# Solo el superusuario puede acceder al panel
@user_passes_test(lambda u: u.is_superuser)
def eliminar_directivo_panel(request):
    notas = NotaDirectivo.objects.all().order_by('-fecha_creacion')
    acuerdos = AcuerdoDirectivo.objects.all().order_by('-fecha_creacion')
    return render(request, 'administrador/directivo_eliminar.html', {
        'notas': notas,
        'acuerdos': acuerdos
    })


# ✅ Eliminar una nota de forma segura (solo POST)
@require_POST
@user_passes_test(lambda u: u.is_superuser)
def eliminar_nota_directivo(request, nota_id):
    nota = get_object_or_404(NotaDirectivo, id=nota_id)
    nota.delete()
    return redirect('eliminar_directivo')


# ✅ Eliminar un acuerdo de forma segura (solo POST)
@require_POST
@user_passes_test(lambda u: u.is_superuser)
def eliminar_acuerdo_directivo(request, acuerdo_id):
    acuerdo = get_object_or_404(AcuerdoDirectivo, id=acuerdo_id)
    acuerdo.delete()
    return redirect('eliminar_directivo')

# ----------------------------------- operativo ------------------------------


# Panel de eliminación Operativo
@user_passes_test(lambda u: u.is_superuser)
def eliminar_operativo_panel(request):
    integrantes = Integrante.objects.all().order_by('nombre_completo')
    notas = Nota.objects.all().order_by('-fecha_creacion')
    acuerdos = AcuerdoOperativo.objects.all().order_by('-fecha_creacion')
    return render(request, 'administrador/operativo_eliminar.html', {
        'integrantes': integrantes,
        'notas': notas,
        'acuerdos': acuerdos
    })

# Eliminar Integrante
@require_POST
@user_passes_test(lambda u: u.is_superuser)
def eliminar_integrante(request, integrante_id):
    integrante = get_object_or_404(Integrante, id=integrante_id)
    integrante.delete()
    return redirect('eliminar_operativo_panel')

# Eliminar Nota
@require_POST
@user_passes_test(lambda u: u.is_superuser)
def eliminar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id)
    nota.delete()
    return redirect('eliminar_operativo_panel')

# Eliminar Acuerdo Operativo
@require_POST
@user_passes_test(lambda u: u.is_superuser)
def eliminar_acuerdo(request, acuerdo_id):
    acuerdo = get_object_or_404(AcuerdoOperativo, id=acuerdo_id)
    acuerdo.delete()
    return redirect('eliminar_operativo_panel')



# ------------------- usuarios --------------------------



# Ver usuarios
def gestionar_usuarios(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta sección")
        return redirect('home')

    usuarios = User.objects.all()
    return render(request, 'gestionar_usuarios.html', {'usuarios': usuarios})

# Editar usuario
def editar_usuario(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta sección")
        return redirect('home')

    usuario = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        nuevo_nombre = request.POST.get('username')
        nueva_contrasena = request.POST.get('password')

        usuario.username = nuevo_nombre
        if nueva_contrasena:
            usuario.set_password(nueva_contrasena)
        usuario.save()
        messages.success(request, "Usuario actualizado correctamente")
        return redirect('gestionar_usuarios')

    return render(request, 'editar_usuario.html', {'usuario': usuario})

# Eliminar usuario
def eliminar_usuario(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permisos para acceder a esta sección")
        return redirect('home')

    usuario = get_object_or_404(User, id=user_id)
    usuario.delete()
    messages.success(request, "Usuario eliminado correctamente")
    return redirect('gestionar_usuarios')
