from django.db import models
from usuarios.models import Cliente, Mype

# Create your models here.
class Pedido(models.Model):
    fechaEntrega = models.DateTimeField()
    fechaRecoleccion = models.DateTimeField()
    notas = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=15, default='Por entregar')
    pagoRecibido = models.FloatField(blank=True, null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True)
    mype = models.ForeignKey(Mype, on_delete=models.CASCADE, blank=True, null=True)

class CargoExtra(models.Model):
    concepto = models.CharField(max_length=60)
    precio = models.FloatField()
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)