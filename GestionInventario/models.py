from django.db import models
from usuarios.models import Mype, Cliente
from gestionPedidos.models import Pedido

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

    def __str__(self):
        return '%s' % (self.nombre)


class MobiliarioEnMantenimiento(models.Model):
    mobiliario = models.ForeignKey(Mobiliario, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    fechaInicio = models.DateField(auto_now_add=True)
    fechaFin = models.DateField(null=True, blank=True)

class MobiliarioPerdido(models.Model):
    mobiliario = models.ForeignKey(Mobiliario, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    totalReposicion = models.FloatField(blank=True, null=True)
    pagoRecibido = models.FloatField(blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)


##Agregado en el incremento 4 para el modulo de gestion de pedidos
class MobiliarioRentado(models.Model):
    cantidad = models.PositiveIntegerField()
    precio = models.FloatField()
    mobiliario = models.ForeignKey(Mobiliario, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)