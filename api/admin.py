from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado, Producto, ImagenProducto

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
    list_display = ('nombre', 'codigo', 'material', 'edad_recomendada', 'precio', 'stock', 'esta_activo', 'fecha_creacion', 'descuento_para_miembros')
    list_filter = ('material', 'tipo_aprendizaje', 'esta_activo')
    search_fields = ('nombre', 'codigo', 'descripcion')
    list_editable = ('precio', 'stock', 'esta_activo', 'descuento_para_miembros')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'descripcion', 'esta_activo')
        }),
        ('Detalles del Producto', {
            'fields': ('material', 'edad_recomendada', 'tipo_aprendizaje')
        }),
        ('Información Económica', {
            'fields': ('precio', 'descuento_para_miembros', 'stock')
        }),
    )

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

