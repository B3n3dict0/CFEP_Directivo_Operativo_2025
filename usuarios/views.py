from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def menu_usuario(request):
    return render(request, 'usuarios/menu.html')
