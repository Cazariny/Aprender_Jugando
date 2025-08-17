from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BlogCategory, BlogPost, UsuarioPersonalizado, Producto,ImagenProducto,Resena, Carrito, Orden, ItemCarrito, ItemOrden, MensajeContacto
from django.db import IntegrityError
@admin.register(UsuarioPersonalizado)
class UsuarioPersonalizadoAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_membresia', 'esta_verificado', 'is_staff')
    list_filter = ('tipo_membresia', 'esta_verificado', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'email_institucional')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {
            'fields': ('tipo_membresia', 'esta_verificado', 'documento_verificacion', 'email_institucional'),
        }),
    )

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'material', 'precio', 'stock', 
                   'esta_activo', 'fecha_creacion', 'descuento_para_miembros', 'edad_recomendada_min', 'edad_recomendada_max')
    list_filter = ('material', 'tipo_aprendizaje', 'esta_activo')
    search_fields = ('nombre', 'codigo', 'descripcion')
    list_editable = ('precio', 'stock', 'esta_activo', 'descuento_para_miembros', 'edad_recomendada_min', 'edad_recomendada_max')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'descripcion', 'esta_activo')
        }),
        ('Detalles del Producto', {
            'fields': ('material', 'tipo_aprendizaje', 'edad_recomendada_min', 'edad_recomendada_max')
        }),
        ('Información Económica', {
            'fields': ('precio', 'descuento_para_miembros', 'stock')
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Completely defensive save handling with transaction management
        """
        from django.db import transaction
        try:
            with transaction.atomic():
                obj.save()
                
                if hasattr(form, 'save_m2m'):
                    form.save_m2m()
                    
        except IntegrityError as e:
            if 'FOREIGN KEY' in str(e):
                obj.save(force_insert=True)
                if hasattr(form, 'save_m2m'):
                    form.save_m2m()
            else:
                raise
            
@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'imagen', 'es_principal', 'orden')
    list_filter = ('es_principal',)
    search_fields = ('producto__nombre', 'producto__codigo')
    list_editable = ('es_principal', 'orden')

    from django.contrib import admin
from .models import Resena, Carrito

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'usuario', 'calificacion', 'fecha_creacion', 'fecha_actualizacion')
    list_filter = ('calificacion', 'fecha_creacion')
    search_fields = ('producto__nombre', 'usuario__username', 'comentario')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('-fecha_creacion',)
@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_creacion', 'fecha_actualizacion', 'total_items', 'total')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'total_items', 'total')

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Total Items'

    def total(self, obj):
        return obj.total
    total.short_description = 'Total'

class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'carrito', 'producto', 'cantidad', 'subtotal_calculado')
    list_filter = ('carrito__usuario', 'producto')
    search_fields = ('carrito__usuario__username', 'producto__nombre')
    
    def subtotal_calculado(self, obj):
        return f"${obj.subtotal:.2f}"
    subtotal_calculado.short_description = 'Subtotal'

class OrdenAdmin(admin.ModelAdmin):
    list_display = (
        'numero_orden',
        'usuario',
        'estado',
        'metodo_pago',
        'total',
        'fecha_creacion',
        'email_enviado'
    )
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion', 'email_enviado')
    search_fields = ('numero_orden', 'usuario__username', 'usuario__email')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('-fecha_creacion',)

admin.site.register(ItemCarrito, ItemCarritoAdmin)
admin.site.register(Orden, OrdenAdmin)

class ItemOrdenAdmin(admin.ModelAdmin):
    list_display = ('orden', 'producto', 'cantidad', 'precio', 'subtotal')
    list_filter = ('orden', 'producto')
    search_fields = ('producto__nombre', 'orden__id')
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Subtotal'

@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'fecha_creacion', 'esta_respondido')
    list_filter = ('esta_respondido', 'fecha_creacion')
    search_fields = ('nombre', 'email', 'mensaje')
    
class AdministrarBlogCategory(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    list_filter = ('nombre', 'slug')
    search_fields = ('nombre', 'slug')
admin.site.register(BlogCategory, AdministrarBlogCategory)
    
class AdministrarBlogPost(admin.ModelAdmin):
    list_display = ('titulo', 'slug', 'autor')
    list_filter = ('titulo', 'autor', 'categoria')
    search_fields = ('titulo', 'autor', 'categoria')
admin.site.register(BlogPost, AdministrarBlogPost)