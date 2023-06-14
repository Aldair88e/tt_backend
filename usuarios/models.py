from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.

class Usuario(AbstractUser):
    is_mype = models.BooleanField(default=False)
    have_data = models.BooleanField(default=False)


class Direccion(models.Model):
    codigoPostal = models.CharField(max_length=5)
    numInterior = models.CharField(max_length=15, blank=True)
    numExterior = models.CharField(max_length=15)
    calle = models.CharField(max_length=60)
    colonia = models.CharField(max_length=60)
    ciudad = models.CharField(max_length=60)
    estado = models.CharField(max_length=60)
    referencia = models.TextField(blank=True)

    def __str__(self):
        return '%s, %s, %s, %s, %s' % (self.calle, self.numExterior, self.colonia, self.ciudad, self.estado)
# class Cliente_tiene_Direccion():

class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    apellido1 = models.CharField(max_length=40)
    apellido2 = models.CharField(max_length=40, blank=True)
    telefono = models.CharField(max_length=10)
    is_web = models.BooleanField(default=False)
    direcciones = models.ManyToManyField(Direccion, blank=True)

    def __str__(self):
        return '%d %s %s' % (self.id, self.nombre, self.apellido1)

class Mype(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True
    )
    nombreEmpresa = models.CharField(max_length=50)
    horaApertura = models.CharField(max_length=10)
    horaCierre = models.CharField(max_length=10)
    descripcion = models.TextField()
    telefono = models.CharField(max_length=10)
    direcciones = models.ManyToManyField(Direccion, blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    imagen = models.ImageField(default='img/default.jpg', upload_to= 'img/')

class ClienteWeb(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

class ClientePorTelefono(models.Model):
    cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    mype = models.ForeignKey(Mype, on_delete=models.CASCADE)