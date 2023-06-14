from rest_framework import serializers
from .models import CargoExtra, Pedido
from GestionInventario.serializers import MobiliarioRentadoSerializer, GetMobiliarioRentadoSerializer
from gestionClientes.serializers import GetClienteSerializer, ClienteEnPedidoSerializer
from usuarios.models import Mype
from usuarios.serializers import DireccionSerializer

class CargoExtraSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = CargoExtra
        fields = ['id', 'concepto', 'precio']
        read_only_fields = ['id']

class CargoExtraPostSerializer(serializers.ModelSerializer):
    pedido = serializers.IntegerField()
    class Meta: 
        model = CargoExtra
        fields = ['concepto', 'precio', 'pedido']

class CargoExtraOnPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoExtra
        fields = ['concepto', 'precio']

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['fechaEntrega', 'fechaRecoleccion', 'notas', 'estado', 'pagoRecibido']

class PedidoSerializerOnPut(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Pedido
        fields = ['fechaEntrega', 'fechaRecoleccion', 'notas', 'estado', 'id', 'pagoRecibido']
        read_only_fields = ['id']

class PedidoRegistroSerializer(serializers.Serializer):
    pedido = PedidoSerializer()
    cliente = serializers.IntegerField()
    cargosExtra = CargoExtraOnPedidoSerializer(many = True)
    mobiliarioRentado = MobiliarioRentadoSerializer(many = True)

class PedidoGetSerializer(serializers.ModelSerializer):
    cliente = GetClienteSerializer()
    class Meta:
        model = Pedido
        fields = ['cliente', 'fechaEntrega', 'fechaRecoleccion', 'notas', 'estado', 'id', 'pagoRecibido']
        read_only_fields = ['cliente', 'id']
class PedidoParaListaSerializer(serializers.ModelSerializer):
    cliente = ClienteEnPedidoSerializer()
    total_mobiliario = serializers.FloatField()
    total_cargos = serializers.FloatField()
    class Meta:
        model = Pedido
        fields = ['id', 'cliente', 'fechaEntrega', 'fechaRecoleccion', 'total_mobiliario', 'total_cargos', 'pagoRecibido','estado', 'notas']
        read_only_fields = ['id', 'cliente', 'total_mobiliario', 'total_cargos']

class PedidoConMobiliarioRentadoSerializer(serializers.ModelSerializer):
    mobiliariorentado_set = GetMobiliarioRentadoSerializer(many =True, read_only = True)
    cliente = serializers.StringRelatedField()
    class Meta:
        model = Pedido
        fields = ['cliente', 'fechaEntrega', 'fechaRecoleccion', 'mobiliariorentado_set']

class PedidoParaHistorialClienteSerializer(serializers.ModelSerializer):
    total_mobiliario = serializers.FloatField()
    total_cargos = serializers.FloatField()
    class Meta:
        model = Pedido
        fields = ['id', 'fechaEntrega', 'fechaRecoleccion', 'total_mobiliario', 'total_cargos', 'pagoRecibido','estado']
        read_only_fields = ['id', 'total_mobiliario', 'total_cargos']



class MypeParaPedidoSerializer(serializers.ModelSerializer):
    direcciones = DireccionSerializer(many=True)
    class Meta:
        model = Mype
        fields = ['nombreEmpresa', 'telefono', 'direcciones', 'usuario_id']

class PedidoParaClienteSerializer(serializers.ModelSerializer):
    mype = MypeParaPedidoSerializer()
    class Meta:
        model = Pedido
        fields = ['fechaEntrega', 'fechaRecoleccion', 'estado', 'id', 'mype']
