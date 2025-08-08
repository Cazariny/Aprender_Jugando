from django.views.generic import DetailView
from django.db.models import F
from .models import BlogPost, BlogCategory, Producto, Carrito, ItemCarrito, Carrito
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from api.models import UsuarioPersonalizado  
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect




def About(request):
    return render(request, "pages/about.html")

def BlogCategory(request):
    # Obtener todos los posts publicados ordenados por fecha (más recientes primero)
    posts = BlogPost.objects.filter(es_publicado=True).order_by('-fecha_publicacion')
    
    # Filtrar por categoría si se especifica
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(categoria__slug=category_slug)
    
    # Obtener todas las categorías para los filtros
    # categories = BlogCategory.objects.all()
    
    # Preparar el contexto
    context = {
        'posts': posts,
    }
    
    # Añadir información de la categoría activa si hay filtro
    if category_slug:
        active_category = get_object_or_404(BlogCategory, slug=category_slug)
        context['active_category'] = category_slug
        context['active_category_name'] = active_category.nombre  # Cambiado de name a nombre
    
    return render(request, "blog/blog.html", context)


def BlogDetail(request, slug):
    # Obtener el post publicado o mostrar 404 si no existe o no está publicado
    post = get_object_or_404(BlogPost, slug=slug, es_publicado=True)
    
    # Incrementar el contador de vistas
    BlogPost.objects.filter(pk=post.pk).update(vistas=F('vistas') + 1)
    post.refresh_from_db()  # Actualizar el objeto con el nuevo valor de vistas
    
    return render(request, "blog/blog_detail.html", {'post': post})



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

    return render(request, 'usuarios/login.html')




def logout_view(request):
    logout(request)
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

    return render(request, 'usuarios/registro.html')

def catalogo(request):
    productos = Producto.objects.filter(esta_activo=True)
    
    # Filtros
    edad = request.GET.getlist('edad')
    tipo_aprendizaje = request.GET.getlist('tipo')
    precio = request.GET.get('precio')
    
    if edad:
        edad_query = Q()
        for rango in edad:
            if '-' in rango:
                min_age, max_age = map(int, rango.split('-'))
                edad_query |= Q(edad_recomendada__contains=f"{min_age}-{max_age}")
            else:
                edad_query |= Q(edad_recomendada__contains=rango)
        productos = productos.filter(edad_query)
    
    if tipo_aprendizaje:
        productos = productos.filter(tipo_aprendizaje__in=tipo_aprendizaje)
    
    if precio:
        min_price, max_price = map(float, precio.split('-'))
        productos = productos.filter(precio__gte=min_price, precio__lte=max_price)
    
    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(productos, 12)  # 12 productos por página
    
    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)
    
    context = {
        'productos': productos_paginados,
        'age_ranges': ['1-3', '3-6', '6-9', '9-12'],
        'tipos_aprendizaje': Producto.OPCIONES_TIPO_APRENDIZAJE,
    }
    return render(request, 'products/catalogo.html', context)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, esta_activo=True)
    
    # Calcular precio con descuento si es miembro educativo
    precio_con_descuento = None
    if request.user.is_authenticated and request.user.es_miembro_educativo():
        descuento = producto.descuento_para_miembros / 100
        precio_con_descuento = producto.precio * (1 - descuento)
    
    context = {
        'producto': producto,
        'precio_con_descuento': precio_con_descuento,
        'resenas': producto.resenas.all().order_by('-fecha_creacion'),
    }
    return render(request, 'products/producto.html', context)

def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Obtener o crear el carrito del usuario
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        
        # Agregar o actualizar el item en el carrito
        item, item_created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        
        if not item_created:
            item.cantidad += cantidad
            item.save()
        
       # return redirect('carrito')


@login_required
def vista_carrito(request):
    try:
        carrito = Carrito.objects.get(usuario=request.user)
        items = ItemCarrito.objects.filter(carrito=carrito).select_related('producto')
    except Carrito.DoesNotExist:
        carrito = None
        items = []

    # Opcional: calcular subtotal por item
    for item in items:
        item.subtotal = item.producto.precio * item.cantidad

    # Opcional: totales del carrito
    if carrito:
        carrito.subtotal = sum(item.subtotal for item in items)
        carrito.envio = 5.99
        # No asignar carrito.total

    return render(request, 'carrito/carrito.html', {
        'carrito': carrito,
        'items': items
    })


    

