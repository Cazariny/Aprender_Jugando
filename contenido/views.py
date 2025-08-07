from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from api.models import UsuarioPersonalizado  
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def home(request):
    print("Usuario logueado:", request.user)
    return render(request, 'pages/home.html')

def about(request):
    return render(request, 'pages/about.html')

def login(request):
    return render(request, 'usuarios/login.html')

def registro(request):
    return render(request, "usuarios/registro.html")