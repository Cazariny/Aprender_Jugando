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
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "Has iniciado sesión correctamente.")
            return redirect('home')
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
            return redirect('login')

    return render(request, 'pages/login.html')




def logout(request):
    auth_logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('home')


def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        tipo_form = request.POST.get('tipo')  # 'estandar' o 'docente'

        tipo_membresia = 'regular' if tipo_form == 'estandar' else 'teacher'

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('registro')

        if UsuarioPersonalizado.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect('registro')

        if UsuarioPersonalizado.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está en uso.")
            return redirect('registro')

        try:
            usuario = UsuarioPersonalizado.objects.create_user(
                username=username,
                email=email,
                password=password1,
                tipo_membresia=tipo_membresia,
                first_name=first_name,
                last_name=last_name,
            )

            # Ahora autenticar para login automático:
            user = authenticate(request, email=email, password=password1)
            if user is not None:
                auth_login(request, user, backend='api.auth_backends.EmailBackend')
                messages.success(request, "Usuario registrado correctamente e iniciado sesión.")
                return redirect('home')
            else:
                messages.error(request, "Error al iniciar sesión automáticamente. Intenta iniciar sesión manualmente.")
                return redirect('login')

        except Exception as e:
            messages.error(request, f"Error durante el registro: {e}")
            return redirect('registro')

    return render(request, 'pages/registro.html')