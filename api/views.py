from django.views.generic import DetailView
from django.db.models import F
from .models import BlogPost, BlogCategory, Producto, Carrito, ItemCarrito, Carrito, Resena
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
from django.views.decorators.http import require_POST





def About(request):
    return render(request, "pages/about.html")

def BlogCategory(request):
    posts = BlogPost.objects.filter(es_publicado=True).order_by('-fecha_publicacion')
    
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(categoria__slug=category_slug)
    
    
    context = {
        'posts': posts,
    }
    
    if category_slug:
        active_category = get_object_or_404(BlogCategory, slug=category_slug)
        context['active_category'] = category_slug
        context['active_category_name'] = active_category.nombre  
    
    return render(request, "blog/blog.html", context)

def BlogDetail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, es_publicado=True)

    if not request.user.is_authenticated or not request.user.tipo_Membresia == 'premium':
        messages.info(request, 'Este contenido es solo para miembros premium. Por favor, inicia sesión o actualiza tu membresía para verlo.')
        return redirect('Blog')

    BlogPost.objects.filter(pk=post.pk).update(vistas=F('vistas') + 1)
    post.refresh_from_db()  
    
    return render(request, "blog/blog_detail.html", {'post': post})

def membresia(request):
    return render(request, "membresia/membresia.html")

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
        tipo_form = request.POST.get('tipo')  

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

@login_required
def perfil(request):
    total_reseñas = Resena.objects.filter(usuario=request.user).count()
    reseñas_usuario = Resena.objects.filter(usuario=request.user).select_related('producto')

    context = {
        'total_reseñas': total_reseñas,
        'reseñas_usuario': reseñas_usuario,
    }
    return render(request, 'usuarios/perfil.html', context)



@login_required
def mis_pedidos(request):
    pedidos = [] 
    return render(request, 'usuarios/mis_pedidos.html', {'pedidos': pedidos})

def mis_resenas(request):
    reseñas_usuario = Resena.objects.filter(usuario=request.user)
    
    return render(request, 'products/mis_resenas.html', {
        'reseñas_usuario': reseñas_usuario
    })

@login_required
def configuracion(request):
    return render(request, 'usuarios/configuracion.html')

@login_required
def editar_perfil(request):
    usuario = request.user

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        usuario.email = request.POST.get('email')

        try:
            usuario.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('perfil')
        except Exception as e:
            messages.error(request, f"Error al actualizar: {e}")
            return redirect('editar_perfil')

    return render(request, 'usuarios/editar_perfil.html', {'usuario': usuario})

def catalogo(request):
    productos = Producto.objects.filter(esta_activo=True)
    
    edad = request.GET.getlist('edad')
    tipo_aprendizaje = request.GET.getlist('tipo')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    filters = Q()
    
    if edad:
        edad_query = Q()
        for rango in edad:
            if rango.startswith("{'value':"):
                try:
                    import ast
                    rango_dict = ast.literal_eval(rango)
                    rango_val = rango_dict['value']
                except:
                    continue
            else:
                rango_val = rango
                
            if '-' in rango_val:
                try:
                    min_age, max_age = map(int, rango_val.split('-'))
                    edad_query |= Q(edad_recomendada_min__lte=max_age, edad_recomendada_max__gte=min_age)
                except ValueError:
                    continue
            else:
                try:
                    edad_query |= Q(edad_recomendada_min__lte=int(rango_val), edad_recomendada_max__gte=int(rango_val))
                except ValueError:
                    continue
        
        filters &= edad_query
    
    if tipo_aprendizaje:
        filters &= Q(tipo_aprendizaje__in=tipo_aprendizaje)
    
    if precio_min:
        try:
            filters &= Q(precio__gte=float(precio_min))
        except (ValueError, TypeError):
            pass
    
    if precio_max:
        try:
            filters &= Q(precio__lte=float(precio_max))
        except (ValueError, TypeError):
            pass
    
    productos = productos.filter(filters)
    
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    
    page = request.GET.get('page', 1)
    paginator = Paginator(productos, 12)
    
    try:
        productos_paginados = paginator.page(page)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)
    
    context = {
        'productos': productos_paginados,
        'age_ranges': [
            {'value': '1-3', 'label': '1-3 años'},
            {'value': '3-6', 'label': '3-6 años'},
            {'value': '6-9', 'label': '6-9 años'},
            {'value': '9-12', 'label': '9-12 años'},
            {'value': '12-15', 'label': '12-15 años'},
        ],
        'tipos_aprendizaje': Producto.OPCIONES_TIPO_APRENDIZAJE,
        'current_filters': {
            'edad': edad,
            'tipo': tipo_aprendizaje,
            'precio_min': precio_min,
            'precio_max': precio_max,
        },
        'query_params': params.urlencode(),
    }
    return render(request, 'products/catalogo.html', context)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, esta_activo=True)
    
    if request.method == 'POST' and request.user.is_authenticated:
        form_data = request.POST
        calificacion = form_data.get('calificacion')
        comentario = form_data.get('comentario')
        
        if not Resena.objects.filter(producto=producto, usuario=request.user).exists():
            Resena.objects.create(
                producto=producto,
                usuario=request.user,
                calificacion=calificacion,
                comentario=comentario
            )
        else:
            messages.warning(request, 'Ya has enviado una reseña para este producto.')
    
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
        
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
        
        item, item_created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        if not item_created:
            item.cantidad += cantidad
            item.save()
        return redirect('detalle_producto', producto_id=producto.id)  


@login_required
def vista_carrito(request):
    usuario = request.user
    carrito = Carrito.objects.filter(usuario=usuario).first()

    if not carrito:
        return render(request, 'carrito/carrito.html', {
            'carrito': carrito,
            'items': [],
            'subtotal': 0,
            'envio': 0,
            'total': 0
        })

    items = ItemCarrito.objects.filter(carrito=carrito)

    PRECIO_ENVIO = 80
    subtotal = sum(item.producto.precio * item.cantidad for item in items)
    envio = PRECIO_ENVIO
    total = subtotal + envio

    return render(request, 'carrito/carrito.html', {
        'carrito': carrito,
        'items': items,
        'subtotal': subtotal,
        'envio': envio,
        'total': total
    })



@login_required
@require_POST
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    print("Eliminando item:", item.id)
    item.delete()
    return redirect('carrito')


@login_required
def checkout(request):
    carrito = request.session.get('carrito/carrito.hmtl', {})
    
    items = []
    subtotal = 0
    
    for producto_id, item_data in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            cantidad = item_data['cantidad']
            precio_unitario = producto.precio
            subtotal_item = precio_unitario * cantidad
            
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal_item
            })
            
            subtotal += subtotal_item
        except Producto.DoesNotExist:
            continue
    
    envio = max(subtotal * 0.05, 5)
    total = subtotal + envio
    
    context = {
        'items': items,
        'subtotal': subtotal,
        'envio': envio,
        'total': total
    }
    
    return render(request, 'carrito/checkout.html', context)

