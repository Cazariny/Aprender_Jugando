from django.shortcuts import render
from django.views.generic import DetailView
from django.db.models import F
from .models import BlogPost, BlogCategory
from django.db.models import Q
from django.db.models import F
from django.shortcuts import render, get_object_or_404

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