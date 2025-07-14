from django.shortcuts import render
from api.models import (
    Producto, 
)

def home(request):
    return render(request, 'pages/home.html') 
