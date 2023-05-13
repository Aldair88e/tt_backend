from rest_framework import serializers
from .models import Mobiliario, MobiliarioEnMantenimiento, MobiliarioPerdido, MobiliarioRentado

class MobiliarioSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(max_length=None, use_url=True)
    total_mantenimiento = serializers.IntegerField(allow_null=True)
    total_perdido = serializers.IntegerField(allow_null=True)
    total_rentado = serializers.IntegerField(allow_null=True)
    class Meta:
        model = Mobiliario
        fields = ['imagen', 'nombre', 'id', 'total', 'precioCompra', 'precioRenta', 'proveedor', 'total_mantenimiento', 'descripcion', 'total_perdido', 'total_rentado']


class MobiliarioShortSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Mobiliario
        fields = ['id', 'nombre', 'precioRenta', 'precioCompra']
        

class MobiliarioMantenimientoSerializer(serializers.ModelSerializer):
    fechaFin = serializers.DateField(allow_null=True)
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

class MobiliarioPerdidoBaseSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data['totalReposicion'] is not None:
            if data['totalReposicion'] < 0:
                raise serializers.ValidationError("No se permiten valores negativos")
        if data['pagoRecibido'] is not None:
            if data['pagoRecibido'] < 0:
                raise serializers.ValidationError("No se permiten valores negativos")
        return data
    
    class Meta:
        model = MobiliarioPerdido
        exclude = ['mobiliario', 'id', 'cliente', 'fecha']


class MobiliarioPerdidoRegistroSerializer(serializers.Serializer):
    mobiliarioPerdido = MobiliarioPerdidoBaseSerializer()
    mobiliario = serializers.IntegerField()
    cliente =  serializers.IntegerField(allow_null=True)

class MobiliarioPerdidoPutSerializer(serializers.Serializer):
    mobiliarioPerdido = MobiliarioPerdidoBaseSerializer()
    id = serializers.IntegerField()
    
class MobiliarioPerdidoGetSerializer(serializers.ModelSerializer):
    mobiliario = serializers.StringRelatedField() 
    cliente = serializers.StringRelatedField()
    class Meta:
        model = MobiliarioPerdido
        fields = '__all__'
        read_only_fields = ['mobiliario', 'id', 'cliente', 'fecha']

class MobiliarioPerdidoPorClienteSerializer(serializers.ModelSerializer):
    mobiliario = serializers.StringRelatedField()
    class Meta:
        model = MobiliarioPerdido
        exclude = ['cliente']
        read_only_fields = ['mobiliario', 'id', 'fecha']

class MobiliarioRentadoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = MobiliarioRentado
        fields = ['cantidad', 'precio', 'id']
        read_only_fields = ['id']

class MobiliarioRentadoPostSerializer(serializers.ModelSerializer):
    mobiliario = serializers.IntegerField()
    pedido = serializers.IntegerField()
    class Meta:
        model = MobiliarioRentado
        fields = ['cantidad', 'precio', 'mobiliario', 'pedido']



class GetMobiliarioRentadoSerializer(serializers.ModelSerializer):
    mobiliario = serializers.StringRelatedField()
    class Meta:
        model = MobiliarioRentado
        fields = ['cantidad', 'precio', 'id', 'mobiliario']
        read_only_field = ['mobiliario', 'id']

# class MobiliarioRentadoListaSerializer(serializers.ModelSerializer):
#     mobiliario = serializers.StringRelatedField()
#     pedido = PedidoParaMobiliarioSerializer()
#     class Meta:
#         model = MobiliarioRentado
#         fields = ['cantidad', 'mobiliario', 'pedido']
        

