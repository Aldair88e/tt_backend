from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Usuario(AbstractUser):
    is_mype = models.BooleanField(default=False)
    have_data = models.BooleanField(default=False)


class Direccion(models.Model):
    codigoPostal = models.CharField(max_length=5)
    numInterior = models.CharField(max_length=15, blank=True)
    numExterior = models.CharField(max_length=15)
    calle = models.CharField(max_length=40)
    colonia = models.CharField(max_length=40)
    ciudad = models.CharField(max_length=50)
    estado = models.CharField(max_length=30)
    referencia = models.TextField(blank=True)
# class Cliente_tiene_Direccion():

class Cliente(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    nombre = models.CharField(max_length=50)
    apellido1 = models.CharField(max_length=40)
    apellido2 = models.CharField(max_length=40, blank=True)
    telefono = models.CharField(max_length=10)
    direcciones = models.ManyToManyField(Direccion, blank=True)

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