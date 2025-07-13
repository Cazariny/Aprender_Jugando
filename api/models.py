from django.contrib.auth.models import AbstractUser
from django.db import models

class UsuarioPersonalizado(AbstractUser):
    OPCIONES_MEMBRESIA = [
        ('regular', 'Usuario regular'),
        ('teacher', 'Docente'),
        ('institution', 'Institución educativa'),
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
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="usuario_personalizado_set",
        related_query_name="usuario_personalizado",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="usuario_personalizado_set",
        related_query_name="usuario_personalizado",
    )
    
    def es_miembro_educativo(self):
        return self.tipo_membresia in ['teacher', 'institution']
    
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
    edad_recomendada = models.CharField(max_length=50)
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
    
    def promedio_calificacion(self):
        from django.db.models import Avg
        return self.resenas.aggregate(Avg('calificacion'))['calificacion__avg'] or 0
    
    def _str_(self):
        return self.nombre
    
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
