from rest_framework import serializers
from .models import Mobiliario, MobiliarioEnMantenimiento

class MobiliarioSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(max_length=None, use_url=True)
    total_mantenimiento = serializers.IntegerField(allow_null=True)
    class Meta:
        model = Mobiliario
        fields = ['imagen', 'nombre', 'id', 'total', 'precioCompra', 'precioRenta', 'proveedor', 'total_mantenimiento', 'descripcion']


class MobiliarioShortSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Mobiliario
        fields = ['id', 'nombre']
        

class MobiliarioMantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobiliarioEnMantenimiento
        fields = ['cantidad', 'fechaFin', 'fechaInicio']
        read_only_fields = ['fechaInicio']
    

class MobiliarioMantenimientoFullSerializer(serializers.Serializer):
    mobiliario = MobiliarioShortSerializer(partial=True)
    mobiliarioMantenimiento = MobiliarioMantenimientoSerializer()

class MantenimientoOnGetSerializer(serializers.ModelSerializer):
    mobiliario = MobiliarioShortSerializer()
    class Meta:
        model = MobiliarioEnMantenimiento
        fields = '__all__'
        read_only_fields = ['mobiliario', 'id']

class MantenimientoDelete(serializers.Serializer):
    id = serializers.IntegerField()

class MantenimientoPutSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = MobiliarioEnMantenimiento
        fields = ['id', 'cantidad', 'fechaFin']

# class MobiliarioGetInfoSerializer(serializers.Serializer):
#     mobiliario = MobiliarioSerializer()
