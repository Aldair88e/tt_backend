from django.db import models
from usuarios.models import Mype, Cliente, ClienteWeb
from gestionPedidos.models import Pedido
from django.core.validators import MinValueValidator, MaxValueValidator
from GestionInventario.models import Mobiliario


# Create your models here.
class Comentario(models.Model):
    mype = models.ForeignKey(Mype, on_delete=models.CASCADE, related_name="comentarios")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="comentarios_cl")
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    comentario_texto = models.TextField(max_length=500, blank=True, default='')
    calificacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    fecha = models.DateField(auto_now_add=True)

class SolicitudCotizacion(models.Model):
    clienteWeb = models.ForeignKey(ClienteWeb, on_delete=models.CASCADE, related_name="solicitudes_hechas")
    mype = models.ForeignKey(Mype, on_delete=models.CASCADE, related_name="solicitudes_recibidas")
    fechaEntrega = models.DateTimeField()
    fechaRecoleccion = models.DateTimeField()
    estado = models.CharField(max_length=15, default='Por cotizar')

class CargoExtraCotizacion(models.Model):
    concepto = models.CharField(max_length=60)
    precio = models.FloatField()
    solicitud = models.ForeignKey(SolicitudCotizacion, on_delete=models.CASCADE, related_name='cargos')

class MobiliarioPorCotizar(models.Model):
    mobiliario = models.ForeignKey(Mobiliario, on_delete=models.CASCADE, related_name="por_cotizar")
    solicitud = models.ForeignKey(SolicitudCotizacion, on_delete=models.CASCADE, related_name="articulos")
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio = models.FloatField(blank=True, null=True)