from django.shortcuts import render
from datetime import datetime

# Create your views here.
def directivo_view(request):
    context = {'fecha_actual': datetime.now()}
    return render(request, 'directivo/reunion_main.html', context)
