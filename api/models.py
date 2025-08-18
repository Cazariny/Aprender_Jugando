from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class UsuarioPersonalizado(AbstractUser):
    OPCIONES_MEMBRESIA = [
        ('regular', 'Usuario regular'),
        ('premium', 'Usuario Premium'),
    ]

    tipo_membresia = models.CharField(
        max_length=20,
        choices=OPCIONES_MEMBRESIA,
        default='regular'
    )
    esta_verificado = models.BooleanField(default=False)
    documento_verificacion = models.FileField(
        upload_to='documentos_verificacion/',
        null=True,
        blank=True
    )
    email_institucional = models.EmailField(null=True, blank=True)

    # 🏠 Datos de envío integrados
    nombre_envio = models.CharField(max_length=100, blank=True, null=True)
    direccion_envio = models.TextField(blank=True, null=True)
    telefono_envio = models.CharField(max_length=20, blank=True, null=True)
    ciudad_envio = models.CharField(max_length=50, blank=True, null=True)
    codigo_postal_envio = models.CharField(max_length=10, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='El grupo al que pertenece este usuario. El usuario obtendrá todos los permisos que le brinde cada uno de sus grupos.',
        related_name="usuario_personalizado_set",
        related_query_name="usuario_personalizado",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permisos de usuario',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        related_name="usuario_personalizado_set",
        related_query_name="usuario_personalizado",
    )

    def es_miembro_educativo(self):
        return self.tipo_membresia in ['teacher', 'institution']

    def tiene_datos_envio(self):
        return all([
            self.nombre_envio,
            self.direccion_envio,
            self.telefono_envio,
            self.ciudad_envio,
            self.codigo_postal_envio
        ])
    
class Producto(models.Model):
    OPCIONES_MATERIAL = [
        ('madera', 'Madera'),
        ('plastico', 'Plástico'),
        ('tela', 'Tela'),
        ('metal', 'Metal'),
        ('mixto', 'Material mixto'),
    ]
    
    OPCIONES_TIPO_APRENDIZAJE = [
        ('motricidad', 'Motricidad'),
        ('cognitivo', 'Desarrollo cognitivo'),
        ('social', 'Habilidades sociales'),
        ('emocional', 'Inteligencia emocional'),
        ('linguistico', 'Lenguaje'),
    ]
    
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField()
    material = models.CharField(max_length=50, choices=OPCIONES_MATERIAL)
    edad_recomendada_min = models.PositiveIntegerField()
    edad_recomendada_max = models.PositiveIntegerField() 
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    esta_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    tipo_aprendizaje = models.CharField(
        max_length=50,
        choices=OPCIONES_TIPO_APRENDIZAJE,
        null=True,
        blank=True
    )
    descuento_para_miembros = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Porcentaje de descuento para miembros educativos"
    )
    
    @property
    def cantidad_resenas(self):
        return self.resenas.count()
    
    def promedio_calificacion(self):
        from django.db.models import Avg
        return self.resenas.aggregate(Avg('calificacion'))['calificacion__avg'] or 0
    
    def get_estrellas(self):
        promedio = self.promedio_calificacion()
        entero = int(promedio)
        decimal = promedio % 1 >= 0.5
        vacio = 5 - entero - (1 if decimal else 0)
        
        return {
            'enteros': [1] * entero,  # Lista con 'entero' elementos
            'tiene_media': decimal,
            'vacios': [1] * vacio     # Lista con 'vacio' elementos
        }
    
    def get_edad_recomendada(self):
        return f"{self.edad_recomendada_min}-{self.edad_recomendada_max} años"
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='productos/')
    es_principal = models.BooleanField(default=False)
    orden = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        
class Resena(models.Model):
    OPCIONES_CALIFICACION = [
        (1, '1 - Muy malo'),
        (2, '2 - Malo'),
        (3, '3 - Regular'),
        (4, '4 - Bueno'),
        (5, '5 - Excelente'),
    ]
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='resenas'
    ) 
    usuario = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    calificacion = models.PositiveSmallIntegerField(choices=OPCIONES_CALIFICACION)
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('producto', 'usuario')
        ordering = ['-fecha_creacion']
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
    
    def __str__(self):
        return f"Reseña de {self.usuario.username} para {self.producto.nombre}"

class Carrito(models.Model):
    """Carrito de compras de usuario"""
    usuario = models.OneToOneField(
        UsuarioPersonalizado,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.cantidad for item in self.items.all())


class ItemCarrito(models.Model):
    """Items individuales en el carrito de compras"""
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    
    @property
    def subtotal(self):
        if self.carrito.usuario.es_miembro_educativo():
            descuento = self.producto.descuento_para_miembros / 100
            precio_con_descuento = self.producto.precio * (1 - descuento)
            return precio_con_descuento * self.cantidad
        return self.producto.precio * self.cantidad

class Orden(models.Model):
    """Órdenes de compra completadas"""
    OPCIONES_ESTADO = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    OPCIONES_METODO_PAGO = [
        ('credit_card', 'Tarjeta de crédito'),
        ('debit_card', 'Tarjeta de débito'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Transferencia bancaria'),
    ]
    
    usuario = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordenes'
    )
    numero_orden = models.CharField(max_length=20, unique=True)
    estado = models.CharField(
        max_length=20,
        choices=OPCIONES_ESTADO,
        default='pending'
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=OPCIONES_METODO_PAGO
    )
    direccion_envio = models.TextField()
    direccion_facturacion = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    email_enviado = models.BooleanField(default=False)
    
    def __str__(self):
        return self.numero_orden

class ItemOrden(models.Model):
    """Items individuales en una orden de compra"""
    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self):
        return self.precio * self.cantidad

class MensajeContacto(models.Model):
    """Mensajes del formulario de contacto"""
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    esta_respondido = models.BooleanField(default=False)
    
    def _str_(self):
        return f"Mensaje de {self.nombre}"

class BlogCategory(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.nombre

class BlogPost(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    autor = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.SET_NULL,
        null=True
    )
    categoria = models.ManyToManyField(BlogCategory)
    contenido = models.TextField()
    imagen = models.ImageField(
        upload_to='blog/',
        null=True,
        blank=True
    )
    es_publicado = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vistas = models.PositiveIntegerField(default=0)
    solo_miembros = models.BooleanField(default=False)
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ['-fecha_publicacion']



