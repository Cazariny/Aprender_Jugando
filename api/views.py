from django.views.generic import DetailView
from datetime import datetime
from django.db.models import F
from .models import BlogPost, BlogCategory, Producto, Carrito, ItemCarrito, Carrito, Resena, Orden, Comentarios
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
from django.http import JsonResponse
from django.db.models import Value, IntegerField, FloatField,Avg, Count, F, Sum
import uuid
from django.db import transaction
from decimal import Decimal



def terminos_condiciones(request):
    return render(request, 'TYC/terminosCondiciones.html')

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

    if not request.user.is_authenticated or not request.user.tipo_membresia == 'premium':
        messages.info(request, 'Este contenido es solo para miembros premium. Por favor, inicia sesión o actualiza tu membresía para verlo.')
        return redirect('Blog')

    
    if request.method == 'POST':
        if request.user.is_authenticated:
            comentario_contenido = request.POST.get('comentario')
            if comentario_contenido:
                Comentarios.objects.create(
                    post=post,
                    user=request.user,
                    contenido=comentario_contenido
                )
                messages.success(request, 'Comentario publicado exitosamente.')
                return redirect('BlogDetail', slug=post.slug)
        else:
            messages.error(request, 'Debes iniciar sesión para comentar.')
            return redirect('login')

    BlogPost.objects.filter(pk=post.pk).update(vistas=F('vistas') + 1)
    post.refresh_from_db()

    comentarios = Comentarios.objects.filter(post=post).order_by('-created_at')

    return render(request, "blog/blog_detail.html", {
        'post': post,
        'comentarios': comentarios,
    })

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
        tipo_membresia = 'regular'

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
    total_ordenes = Orden.objects.filter(usuario=request.user).count()
    context = {
        'total_reseñas': total_reseñas,
        'reseñas_usuario': reseñas_usuario,
        'total_ordenes': total_ordenes,
    }
    return render(request, 'usuarios/perfil.html', context)


@login_required
def mis_pedidos(request):
    pedidos_usuario = Orden.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, "products/mis_pedidos.html", {"pedidos": pedidos_usuario})
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
            messages.warning(request, 'Ya has enviado una reseña para este producto.', extra_tags='header')
    
    precio_con_descuento = None
    if request.user.is_authenticated:
        if request.user.es_premium() or request.user.es_miembro_educativo():
            descuento = producto.descuento_para_miembros / 100
            precio_con_descuento = producto.precio * (1 - descuento)
    
    context = {
        'producto': producto,
        'precio_con_descuento': precio_con_descuento,
        'resenas': producto.resenas.all().order_by('-fecha_creacion'),
        'es_usuario_premium': request.user.is_authenticated and request.user.es_premium(),
    }
    return render(request, 'products/producto.html', context)

# def agregar_al_carrito(request, producto_id):
#     if request.method == 'POST':
#         producto = get_object_or_404(Producto, id=producto_id)
#         cantidad = int(request.POST.get('cantidad', 1))

#         carrito, created = Carrito.objects.get_or_create(usuario=request.user)

#         item, item_created = ItemCarrito.objects.get_or_create(
#             carrito=carrito,
#             producto=producto,
#             defaults={'cantidad': cantidad}
#         )

#         if not item_created:
#             item.cantidad += cantidad
#             item.save()

#         messages.success(request, 'Producto añadido al carrito.', extra_tags='header')
#         return redirect(request.META.get('HTTP_REFERER', '/'))

def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))

        # 1. Get or create the user's cart
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)

        # 2. Check if the product is already in the cart
        item, item_created = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': 0} # Set defaults to 0 to properly calculate total quantity
        )

        # 3. Calculate total requested quantity and check against stock
        total_cantidad_solicitada = item.cantidad + cantidad
        if total_cantidad_solicitada > producto.stock:
            # Insufficient stock, display an error message
            messages.error(request, f'No puedes agregar más de {producto.stock} unidades de este producto. Solo hay {producto.stock} en stock.', extra_tags='header')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            # 4. Update the item quantity and save
            item.cantidad = total_cantidad_solicitada
            item.save()
            messages.success(request, 'Producto añadido al carrito.', extra_tags='header')
            return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def vista_carrito(request):
    usuario = request.user
    carrito = Carrito.objects.filter(usuario=usuario).first()

    # Si no hay carrito, render vacío
    if not carrito:
        return render(request, 'carrito/carrito.html', {
            'carrito': None,
            'items': [],
            'subtotal': Decimal('0.00'),
            'descuento_total': Decimal('0.00'),
            'envio': Decimal('0.00'),
            'total': Decimal('0.00'),
            'tipo_membresia': getattr(usuario, 'tipo_membresia', 'regular'),
            'es_usuario_miembro': False
        })

    cantidades_temporales = request.session.get('cantidades_temporales', {})
    items = []
    subtotal = Decimal('0.00')
    descuento_total = Decimal('0.00')

    # Validar si el usuario tiene beneficios
    es_usuario_miembro = usuario.is_authenticated and (
        hasattr(usuario, 'es_premium') and usuario.es_premium() or
        hasattr(usuario, 'es_miembro_educativo') and usuario.es_miembro_educativo()
    )

    for item in ItemCarrito.objects.filter(carrito=carrito):
        cantidad = int(cantidades_temporales.get(str(item.id), item.cantidad))
        precio_base = item.producto.precio

        # Aplicar descuento si corresponde
        if es_usuario_miembro and item.producto.descuento_para_miembros:
            porcentaje = item.producto.descuento_para_miembros / Decimal('100')
            precio_unitario = precio_base * (Decimal('1.00') - porcentaje)
            descuento_unitario = precio_base * porcentaje
            descuento_total += descuento_unitario * Decimal(cantidad)
        else:
            precio_unitario = precio_base

        precio_item = precio_unitario * Decimal(cantidad)
        subtotal += precio_item

        items.append({
            'item': item,
            'producto': item.producto,
            'cantidad': cantidad,
            'precio_item': precio_item,
            'imagen_principal': item.producto.imagenes.filter(es_principal=True).first()
        })

    # Envío según tipo de usuario
    envio = Decimal('0.00') if es_usuario_miembro else Decimal('80.00')
    total = subtotal + envio

    return render(request, 'carrito/carrito.html', {
        'carrito': carrito,
        'items': items,
        'subtotal': subtotal,
        'descuento_total': descuento_total,
        'envio': envio,
        'total': total,
        'tipo_membresia': getattr(usuario, 'tipo_membresia', 'regular'),
        'es_usuario_miembro': es_usuario_miembro
    })





@login_required
@require_POST
def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__usuario=request.user)
    print("Eliminando item:", item.id)
    item.delete()
    messages.success(request, 'Se ha eliminado el producto.', extra_tags='header')
    return redirect('carrito')


def generar_numero_orden():
    return str(uuid.uuid4())[:12].replace('-', '').upper()



@login_required
def checkout(request):
    usuario = request.user
    es_usuario_miembro = usuario.es_premium()

    cantidades_temporales = request.session.get('cantidades_temporales', {})
    carrito = Carrito.objects.filter(usuario=usuario).first()
    if not carrito:
        return redirect('vista_carrito')

    items = []
    subtotal = Decimal('0.00')
    descuento_total = Decimal('0.00')

    for item in ItemCarrito.objects.filter(carrito=carrito):
        cantidad = cantidades_temporales.get(str(item.id), item.cantidad)

        # Calcular descuento por unidad si el usuario es premium
        if es_usuario_miembro:
            porcentaje_descuento = item.producto.descuento_para_miembros
            descuento_unitario = item.producto.precio * (porcentaje_descuento / Decimal('100'))
        else:
            descuento_unitario = Decimal('0.00')

        precio_unitario = item.producto.precio - descuento_unitario
        precio_item = precio_unitario * cantidad
        subtotal += precio_item
        descuento_total += descuento_unitario * cantidad

        items.append({
            'producto': item.producto,
            'cantidad': cantidad,
            'precio_unitario': item.producto.precio,
            'descuento_unitario': descuento_unitario,
            'subtotal': precio_item,
            'imagen_principal': item.producto.imagenes.filter(es_principal=True).first()
        })

    PRECIO_ENVIO = Decimal('80.00')
    envio = Decimal('0.00') if es_usuario_miembro else PRECIO_ENVIO
    total = subtotal + envio

    if request.method == 'POST':

        metodo_pago = request.POST.get('metodo_pago', 'credit_card')
        
        # Validación para el método de pago con tarjeta
        if metodo_pago == 'tarjeta':
            numero_tarjeta = request.POST.get('numero_tarjeta')
            expiracion_tarjeta = request.POST.get('expiracion_tarjeta')
            cvv_tarjeta = request.POST.get('cvv_tarjeta')
            
            # Validación: Número de tarjeta (solo 16 dígitos)
            if not numero_tarjeta or not (numero_tarjeta.isdigit() and len(numero_tarjeta) == 16):
                messages.error(request, 'El número de tarjeta no es válido.')
                return redirect('checkout')

            # Validación: CVV (solo 3 dígitos)
            if not cvv_tarjeta or not (cvv_tarjeta.isdigit() and len(cvv_tarjeta) == 3):
                messages.error(request, 'El CVV debe tener 3 dígitos.')
                return redirect('checkout')
                
            # Validación: Fecha de expiración (MM/AA)
            if not expiracion_tarjeta or len(expiracion_tarjeta) != 5:
                messages.error(request, 'La fecha de expiración no es válida.')
                return redirect('checkout')
            
            try:
                mes, anio = map(int, expiracion_tarjeta.split('/'))
                # Los dos últimos dígitos del año
                anio_completo = 2000 + anio
                
                # Validar mes y año
                if not (1 <= mes <= 12):
                    messages.error(request, 'El mes de expiración no es válido.')
                    return redirect('checkout')
                
                # Validar año: del 2018 al 2028
                if not (2018 <= anio_completo <= 2040):
                    messages.error(request, 'El año de expiración no es válido.')
                    return redirect('checkout')

                # Validar que la tarjeta no esté caducada
                # hoy = datetime.now()
                # if anio_completo < hoy.year or (anio_completo == hoy.year and mes < hoy.month):
                #     messages.error(request, 'La tarjeta está caducada.')
                #     return redirect('checkout')
            
            except (ValueError, IndexError):
                messages.error(request, 'Formato de fecha de expiración inválido. Utiliza MM/AA.')
                return redirect('checkout')

        # Si todas las validaciones pasan, se procede con la creación de la orden
        usuario.nombre_envio = request.POST.get('nombre')
        usuario.direccion_envio = request.POST.get('direccion')
        usuario.telefono_envio = request.POST.get('telefono')
        usuario.ciudad_envio = request.POST.get('ciudad')
        usuario.codigo_postal_envio = request.POST.get('codigo_postal')
        usuario.save()

        orden = Orden.objects.create(
            usuario=usuario,
            numero_orden=generar_numero_orden(),
            estado='pending',
            metodo_pago=metodo_pago,
            direccion_envio=usuario.direccion_envio,
            direccion_facturacion=usuario.direccion_envio,
            total=total
        )
        
        # Lógica para reducir el stock de productos
        for item in carrito.items.all():
            item.producto.stock -= item.cantidad
            item.producto.save()

        ItemCarrito.objects.filter(carrito=carrito).delete()
        request.session['cantidades_temporales'] = {}

        return redirect('confirmacion_compra', orden_id=orden.id)

    return render(request, 'carrito/checkout.html', {
        'items': items,
        'subtotal': subtotal,
        'envio': envio,
        'total': total,
        'usuario': usuario,
        'es_usuario_miembro': es_usuario_miembro,
        'descuento_total': descuento_total
    })



@login_required
def actualizar_cantidad(request, item_id):
    if request.method == 'POST':
        try:
            item = ItemCarrito.objects.get(id=item_id, carrito__usuario=request.user)
            nueva_cantidad = int(request.POST.get('cantidad', 1))
            
            # 1. Validación de stock
            if nueva_cantidad > item.producto.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Solo hay {item.producto.stock} unidades de este producto en stock.',
                    'stock_disponible': item.producto.stock
                })

            # 2. Si la validación es exitosa, actualiza la cantidad en la sesión
            if 'cantidades_temporales' not in request.session:
                request.session['cantidades_temporales'] = {}

            request.session['cantidades_temporales'][str(item_id)] = nueva_cantidad
            request.session.modified = True

            # 3. Recalcular subtotales y totales para la respuesta
            carrito = item.carrito
            items = ItemCarrito.objects.filter(carrito=carrito)
            subtotal_total = Decimal('0.00')
            es_usuario_miembro = request.user.es_premium() or request.user.es_miembro_educativo()
            
            for i in items:
                cantidad_actualizada = request.session['cantidades_temporales'].get(str(i.id), i.cantidad)
                precio_base = i.producto.precio
                
                precio_unitario = precio_base
                if es_usuario_miembro and i.producto.descuento_para_miembros:
                    porcentaje = i.producto.descuento_para_miembros / Decimal('100')
                    precio_unitario = precio_base * (Decimal('1.00') - porcentaje)
                
                subtotal_total += precio_unitario * cantidad_actualizada

            subtotal_item = precio_unitario * nueva_cantidad
            
            envio = Decimal('0.00') if es_usuario_miembro else Decimal('80.00')
            total = subtotal_total + envio

            return JsonResponse({
                'success': True,
                'nuevoSubtotal': f"${subtotal_item:.2f}",
                'subtotalTotal': f"${subtotal_total:.2f}",
                'total': f"${total:.2f}",
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})



@login_required
def confirmacion_compra(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    return render(request, 'carrito/confirmacion.html', {'orden': orden})

def contacto(request):
    return render(request, "contacto/contacto.html")

@login_required
def checkout_membresia(request):
    usuario = request.user
    
    PRECIO_MEMBRESIA = 19.99

    if request.method == 'POST':
        with transaction.atomic():
            metodo_pago = request.POST.get('metodo_pago', 'credit_card')
            if metodo_pago == 'tarjeta':
                numero_tarjeta = request.POST.get('numero_tarjeta')
                expiracion_tarjeta = request.POST.get('expiracion_tarjeta')
                cvv_tarjeta = request.POST.get('cvv_tarjeta')
            
            # Validación: Número de tarjeta (solo 16 dígitos)
            if not numero_tarjeta or not (numero_tarjeta.isdigit() and len(numero_tarjeta) == 16):
                messages.error(request, 'El número de tarjeta no es válido.')
                return redirect('checkout_membresia')

            # Validación: CVV (solo 3 dígitos)
            if not cvv_tarjeta or not (cvv_tarjeta.isdigit() and len(cvv_tarjeta) == 3):
                messages.error(request, 'El CVV debe tener 3 dígitos.')
                return redirect('checkout_membresia')
                
            # Validación: Fecha de expiración (MM/AA)
            if not expiracion_tarjeta or len(expiracion_tarjeta) != 5:
                messages.error(request, 'La fecha de expiración no es válida.')
                return redirect('checkout_membresia')
            
            try:
                mes, anio = map(int, expiracion_tarjeta.split('/'))
                # Los dos últimos dígitos del año
                anio_completo = 2000 + anio
                
                # Validar mes y año
                if not (1 <= mes <= 12):
                    messages.error(request, 'El mes de expiración no es válido.')
                    return redirect('checkout_membresia')
                
                # Validar año: del 2018 al 2028
                if not (2018 <= anio_completo <= 2028):
                    messages.error(request, 'El año de expiración no es válido.')
                    return redirect('checkout_membresia')

                # Validar que la tarjeta no esté caducada
                # hoy = datetime.today()
                # if anio_completo < hoy.year or (anio_completo == hoy.year and mes < hoy.month):
                #     messages.error(request, 'La tarjeta está caducada.')
                #     return redirect('checkout_membresia')
            
            except (ValueError, IndexError):
                messages.error(request, 'Formato de fecha de expiración inválido. Utiliza MM/AA.')
                return redirect('checkout_membresia')
            
            orden = Orden.objects.create(
                usuario=usuario,
                numero_orden=generar_numero_orden(),
                estado='completed',  
                metodo_pago=metodo_pago,
                direccion_envio='N/A', 
                direccion_facturacion='N/A', 
                total=PRECIO_MEMBRESIA
            )
            
            usuario.tipo_membresia = 'premium' 
            usuario.save()
            
            messages.success(request, "¡Felicidades! Ahora eres un usuario Premium.")

        return redirect('confirmacion_membresia', orden_id=orden.id)
    
    return render(request, 'membresia/checkout_membresia.html', {
        'total': PRECIO_MEMBRESIA,
        'usuario': usuario,
        'is_membership': True
    })

@login_required
def confirmacion_membresia(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id, usuario=request.user)
    return render(request, 'membresia/confirmacion_membresia.html', {'orden': orden})