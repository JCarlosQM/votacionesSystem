from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from cloudinary.models import CloudinaryField

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    nombres_completos = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombres_completos']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


#Core de uso
class Campaña(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True, verbose_name="¿Campaña activa?")

    def __str__(self):
        return self.titulo

class Lista(models.Model):
    campaña = models.ForeignKey(Campaña, on_delete=models.CASCADE, related_name='listas')
    nombre = models.CharField(max_length=100)
    logo = CloudinaryField('logo', blank=True, null=True)  # cambio aquí
    mensaje = models.TextField(blank=True, help_text="Mensaje principal o lema de campaña")

    def __str__(self):
        return f"{self.nombre} - {self.campaña.titulo}"


#VOTANTES
class Votante(models.Model):
    dni = models.CharField(max_length=8, unique=True)
    ha_votado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.dni})"

class Voto(models.Model):
    votante = models.OneToOneField(Votante, on_delete=models.CASCADE)
    lista = models.ForeignKey('Lista', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.votante} → {self.lista}"