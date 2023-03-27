from django.db import models
from usuarios.models import Mype 

# Create your models here.
class Mobiliario(models.Model):
    nombre = models.CharField(max_length=50)
    total = models.IntegerField()
    descripcion = models.TextField(blank=True, null=True)
    precioCompra = models.FloatField(blank=True, null=True)
    precioRenta = models.FloatField(blank=True, null=True)
    proveedor = models.CharField(max_length=50, blank=True, null=True)
    imagen = models.ImageField(blank=True, null=True, upload_to= 'img/')
    mype = models.ForeignKey(Mype, on_delete=models.CASCADE)


class MobiliarioEnMantenimiento(models.Model):
    mobiliario = models.ForeignKey(Mobiliario, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fechaInicio = models.DateField(auto_now_add=True)
    fechaFin = models.DateField(blank=True)