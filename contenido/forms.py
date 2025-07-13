# from django import forms
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.core.exceptions import ValidationError
# from api.models import UsuarioPersonalizado, Producto, Resena, Orden

# class CustomUserCreationForm(UserCreationForm):
#     email = forms.EmailField(required=True, label="Correo electrónico")
#     first_name = forms.CharField(required=True, label="Nombre")
#     last_name = forms.CharField(required=True, label="Apellido")
    
#     class Meta:
#         model = UsuarioPersonalizado
#         fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 'tipo_membresia')
#         labels = {
#             'tipo_membresia': 'Tipo de cuenta',
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['tipo_membresia'].help_text = "Seleccione el tipo de cuenta que mejor describa su perfil"
        
#         # Establecer placeholders
#         self.fields['email'].widget.attrs.update({'placeholder': 'ejemplo@email.com'})
#         self.fields['first_name'].widget.attrs.update({'placeholder': 'Juan'})
#         self.fields['last_name'].widget.attrs.update({'placeholder': 'Pérez'})
#         self.fields['password1'].widget.attrs.update({'placeholder': '••••••••'})
#         self.fields['password2'].widget.attrs.update({'placeholder': '••••••••'})

# class UserProfileForm(UserChangeForm):
#     password = None  # Eliminamos el campo de contraseña del formulario
    
#     documento_verificacion = forms.FileField(
#         required=False,
#         label="Documento de verificación",
#         help_text="Sube un documento que acredite tu condición de docente o institución educativa"
#     )
    
#     class Meta:
#         model = UsuarioPersonalizado
#         fields = ('first_name', 'last_name', 'email', 'tipo_membresia', 
#                  'documento_verificacion', 'email_institucional')
#         labels = {
#             'first_name': 'Nombre',
#             'last_name': 'Apellido',
#             'email': 'Correo electrónico principal',
#             'tipo_membresia': 'Tipo de membresía',
#             'email_institucional': 'Correo institucional (opcional)',
#         }
#         widgets = {
#             'tipo_membresia': forms.Select(attrs={'disabled': 'disabled'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Si el usuario no es miembro educativo, ocultamos el campo de email institucional
#         if not self.instance.es_miembro_educativo():
#             self.fields.pop('email_institucional')

# class CheckoutForm(forms.Form):
#     METODO_PAGO_CHOICES = [
#         ('credit_card', 'Tarjeta de crédito/débito'),
#         ('paypal', 'PayPal'),
#         ('bank_transfer', 'Transferencia bancaria'),
#     ]
    
#     # Información de envío
#     nombre_completo = forms.CharField(
#         max_length=100,
#         label="Nombre completo",
#         widget=forms.TextInput(attrs={'placeholder': 'Juan Pérez'})
#     )
#     direccion = forms.CharField(
#         widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Calle, número, departamento'}),
#         label="Dirección de envío"
#     )
#     ciudad = forms.CharField(
#         max_length=100,
#         widget=forms.TextInput(attrs={'placeholder': 'Ciudad'})
#     )
#     codigo_postal = forms.CharField(
#         max_length=20,
#         label="Código postal",
#         widget=forms.TextInput(attrs={'placeholder': '12345'})
#     )
#     telefono = forms.CharField(
#         max_length=20,
#         label="Teléfono de contacto",
#         widget=forms.TextInput(attrs={'placeholder': '+1 234 567 890'})
#     )
    
#     # Método de pago
#     metodo_pago = forms.ChoiceField(
#         choices=METODO_PAGO_CHOICES,
#         widget=forms.RadioSelect,
#         initial='credit_card',
#         label="Método de pago"
#     )
    
#     # Información de tarjeta (condicional)
#     numero_tarjeta = forms.CharField(
#         required=False,
#         max_length=19,
#         label="Número de tarjeta",
#         widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456'})
#     )
#     fecha_expiracion = forms.CharField(
#         required=False,
#         max_length=5,
#         label="Fecha de expiración (MM/AA)",
#         widget=forms.TextInput(attrs={'placeholder': 'MM/AA'})
#     )
#     codigo_seguridad = forms.CharField(
#         required=False,
#         max_length=4,
#         label="CVV",
#         widget=forms.TextInput(attrs={'placeholder': '123'})
#     )
#     nombre_tarjeta = forms.CharField(
#         required=False,
#         max_length=100,
#         label="Nombre en la tarjeta",
#         widget=forms.TextInput(attrs={'placeholder': 'JUAN PEREZ'})
#     )
    
#     def clean(self):
#         cleaned_data = super().clean()
#         metodo_pago = cleaned_data.get('metodo_pago')
        
#         # Validar campos de tarjeta si el método de pago es tarjeta de crédito
#         if metodo_pago == 'credit_card':
#             if not cleaned_data.get('numero_tarjeta'):
#                 self.add_error('numero_tarjeta', 'Este campo es requerido para pagos con tarjeta')
#             if not cleaned_data.get('fecha_expiracion'):
#                 self.add_error('fecha_expiracion', 'Este campo es requerido para pagos con tarjeta')
#             if not cleaned_data.get('codigo_seguridad'):
#                 self.add_error('codigo_seguridad', 'Este campo es requerido para pagos con tarjeta')
#             if not cleaned_data.get('nombre_tarjeta'):
#                 self.add_error('nombre_tarjeta', 'Este campo es requerido para pagos con tarjeta')
        
#         return cleaned_data

# class ReviewForm(forms.ModelForm):
#     class Meta:
#         model = Resena
#         fields = ('titulo', 'calificacion', 'comentario')
#         labels = {
#             'titulo': 'Título de tu reseña',
#             'calificacion': 'Calificación',
#             'comentario': 'Comentario',
#         }
#         widgets = {
#             'comentario': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Comparte tu experiencia con este producto...'}),
#             'titulo': forms.TextInput(attrs={'placeholder': '¡Excelente producto!'}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['calificacion'].widget = forms.RadioSelect(
#             choices=Resena.OPCIONES_CALIFICACION
#         )

# class ContactForm(forms.Form):
#     nombre = forms.CharField(
#         max_length=100,
#         widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'})
#     )
#     email = forms.EmailField(
#         widget=forms.EmailInput(attrs={'placeholder': 'tu@email.com'})
#     )
#     asunto = forms.CharField(
#         max_length=100,
#         widget=forms.TextInput(attrs={'placeholder': 'Asunto del mensaje'})
#     )
#     mensaje = forms.CharField(
#         widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Escribe tu mensaje aquí...'})
#     )

# class PasswordResetRequestForm(forms.Form):
#     email = forms.EmailField(
#         label="Correo electrónico",
#         widget=forms.EmailInput(attrs={'placeholder': 'tu@email.com'})
#     )

# class SetNewPasswordForm(forms.Form):
#     new_password1 = forms.CharField(
#         label="Nueva contraseña",
#         widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
#     )
#     new_password2 = forms.CharField(
#         label="Confirmar nueva contraseña",
#         widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
#     )
    
#     def clean(self):
#         cleaned_data = super().clean()
#         password1 = cleaned_data.get('new_password1')
#         password2 = cleaned_data.get('new_password2')
        
#         if password1 and password2 and password1 != password2:
#             self.add_error('new_password2', 'Las contraseñas no coinciden')
        
#         return cleaned_data

# class ProductSearchForm(forms.Form):
#     query = forms.CharField(
#         required=False,
#         label="Buscar productos",
#         widget=forms.TextInput(attrs={'placeholder': 'Buscar...'})
#     )
#     categoria = forms.ModelChoiceField(
#         required=False,
#         queryset=Producto.objects.none(),  # Se actualizará en la vista
#         label="Categoría",
#         empty_label="Todas las categorías"
#     )
#     precio_min = forms.DecimalField(
#         required=False,
#         label="Precio mínimo",
#         widget=forms.NumberInput(attrs={'placeholder': 'Mínimo'})
#     )
#     precio_max = forms.DecimalField(
#         required=False,
#         label="Precio máximo",
#         widget=forms.NumberInput(attrs={'placeholder': 'Máximo'})
#     )
    
#     def __init__(self, *args, **kwargs):
#         categorias = kwargs.pop('categorias', None)
#         super().__init__(*args, **kwargs)
#         if categorias:
#             self.fields['categoria'].queryset = categorias