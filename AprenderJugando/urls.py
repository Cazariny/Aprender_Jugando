"""
URL configuration for AprenderJugando project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from contenido import views
from api import views as views_api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('acerca/', views.about, name='acerca'),
    path('blog/', views_api.BlogCategory, name='Blog'),
    path('blog/<slug:slug>', views_api.BlogDetail, name='BlogDetail'),
    path('login/', views_api.login, name='login'),       
    path('logout/', views_api.logout_view, name='logout'), 
    path('registro/', views_api.registro, name='registro'),
    path('membresia/', views_api.membresia, name='membresia'),  
    path('contacto/', views_api.contacto, name='contacto'),  
    path('catalogo/', views_api.catalogo, name='catalogo'),
    path('producto/<int:producto_id>/', views_api.detalle_producto, name='detalle_producto'),
    path('agregar-al-carrito/<int:producto_id>/', views_api.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views_api.vista_carrito, name='carrito'),
    path('carrito/eliminar/<int:item_id>/', views_api.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views_api.checkout, name='checkout'),
    path('perfil/', views_api.perfil, name='perfil'),
    path('perfil/editar/', views_api.editar_perfil, name='editar_perfil'),
    path('mis-pedidos/', views_api.mis_pedidos, name='mis_pedidos'),
    path('mis-resenas/', views_api.mis_resenas, name='mis_resenas'),
    path('perfil/mis_resenas/', views_api.mis_resenas, name='mis_resenas'),
    path('configuracion/', views_api.configuracion, name='configuracion'),  
    path('actualizar-cantidad/<int:item_id>/', views_api.actualizar_cantidad, name='actualizar_cantidad'),
    path('confirmacion/<int:orden_id>/', views_api.confirmacion_compra, name='confirmacion_compra'),
    path('top10/', views.top10, name='top10'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)