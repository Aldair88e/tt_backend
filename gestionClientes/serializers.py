from rest_framework import serializers
from usuarios.models import ClientePorTelefono, Cliente
from usuarios.serializers import RegistroClienteSerializer, DireccionPutSerializer
from GestionInventario.serializers import MobiliarioPerdidoPorClienteSerializer

class CrearClienteSerializer(RegistroClienteSerializer):
    descuento = serializers.FloatField(required=False)

class PutClienteporTelSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Cliente
        exclude = ['direcciones', 'is_web']

class ModificarClienteSerializer(serializers.Serializer):
    cliente = PutClienteporTelSerializer()
    direcciones =  DireccionPutSerializer(many=True)
    descuento = serializers.FloatField(required=False, allow_null=True)

class GetClienteSerializer(serializers.ModelSerializer):
    direcciones = DireccionPutSerializer(many=True)
    class Meta:
        model = Cliente
        fields = '__all__'

class ClienteParaListaSerializer(serializers.ModelSerializer):
    mobiliario_perdido = serializers.IntegerField(allow_null=True)
    mobPerdido_adeudo = serializers.FloatField(allow_null=True)
    mobPerdido_pagado = serializers.FloatField(allow_null=True)
    total_pedidos = serializers.IntegerField(allow_null=True)
    direcciones = DireccionPutSerializer(many=True)
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellido1', 'telefono', 'is_web', 'mobiliario_perdido', 'mobPerdido_adeudo','mobPerdido_pagado', 'direcciones', 'total_pedidos']

class ClienteShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellido1']
        read_only_fields = ['id']

class ClienteEnPedidoSerializer(serializers.ModelSerializer):
    direcciones = DireccionPutSerializer(many=True)
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellido1', 'direcciones']
