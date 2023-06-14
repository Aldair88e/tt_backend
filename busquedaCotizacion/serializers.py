from rest_framework import serializers
from usuarios.models import Mype, Direccion, ClienteWeb, Cliente, Direccion
from GestionInventario.models import Mobiliario
from .models import Comentario, SolicitudCotizacion, MobiliarioPorCotizar, CargoExtraCotizacion
from .utils import mobiliarioDisponibleEnPeriodo
from gestionPedidos.models import Pedido

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ['ciudad', 'codigoPostal', 'estado']

class MypeListaSerializer(serializers.ModelSerializer):
    promedio_calificaciones = serializers.FloatField(allow_null=True)
    total_comentarios = serializers.IntegerField(allow_null=True)
    imagen = serializers.ImageField(max_length=None, use_url=True)
    direcciones = DireccionSerializer(many =True)
    class Meta:
        model = Mype
        fields = ['usuario_id','imagen', 'nombreEmpresa', 'direcciones', 'promedio_calificaciones', 'total_comentarios']
        read_only_fields = ['usuario_id']

class DireccionFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ['codigoPostal', 'numInterior', 'numExterior', 'calle', 'colonia', 'ciudad', 'estado', 'referencia']


class MypeSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(max_length=None, use_url=True)
    direcciones = DireccionSerializer(many =True)
    class Meta:
        model = Mype
        fields = ['usuario_id','imagen', 'nombreEmpresa', 'direcciones', 'horaApertura', 'horaCierre', 'facebook', 'twitter', 'instagram', 'telefono', 'descripcion']
        read_only_fields = ['usuario_id']

class MobiliarioSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(max_length=None, use_url=True)
    class Meta:
        model = Mobiliario
        fields = ['nombre', 'total', 'descripcion', 'id', 'imagen']
        read_only_fields = ['id']

class ComentarioSerializer(serializers.ModelSerializer):
    cliente = serializers.StringRelatedField()
    class Meta:
        model = Comentario
        fields = ['cliente', 'comentario_texto', 'calificacion', 'fecha']


class SolicitudCotizacionSerializer(serializers.ModelSerializer):
    mype = serializers.PrimaryKeyRelatedField(queryset=Mype.objects.all())
    clienteWeb = serializers.PrimaryKeyRelatedField(queryset=ClienteWeb.objects.all())
    class Meta:
        model = SolicitudCotizacion
        fields = '__all__'

class MobiliarioPorCotizarSerializer(serializers.ModelSerializer):
    mobiliario = serializers.PrimaryKeyRelatedField(queryset=Mobiliario.objects.all())
    solicitud = serializers.PrimaryKeyRelatedField(queryset=SolicitudCotizacion.objects.all())
    class Meta:
        model = MobiliarioPorCotizar
        fields = ['cantidad', 'mobiliario', 'solicitud']

class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        exclude = ['id']


class ClienteSerializer(serializers.ModelSerializer):
    direcciones = DireccionSerializer(many=True)
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellido1', 'apellido2', 'telefono', 'direcciones']

class ClienteWebSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    class Meta:
        model = ClienteWeb
        fields = ['cliente']

class SolicitudMypeViewSerializer(serializers.ModelSerializer):
    clienteWeb = ClienteWebSerializer()
    class Meta:
        model = SolicitudCotizacion
        exclude = ['mype']

class MypeShortSerializer(serializers.ModelSerializer):
    direcciones = DireccionFullSerializer(many=True)
    class Meta:
        model = Mype
        fields = ['nombreEmpresa', 'telefono', 'direcciones', 'usuario_id']

class SolicitudClienteViewSerializer(serializers.ModelSerializer):
    mype = MypeShortSerializer()
    class Meta:
        model = SolicitudCotizacion
        exclude = ['clienteWeb']

class MobiliarioOnGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mobiliario
        fields = ['nombre', 'id', 'precioRenta']
class MobiliarioPorCotizarGetSerializer(serializers.ModelSerializer):
    mobiliario = MobiliarioOnGetSerializer()
    class Meta:
        model = MobiliarioPorCotizar
        fields = ['mobiliario', 'cantidad', 'precio', 'id']

class CargoCotizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoExtraCotizacion
        fields = ['id', 'concepto', 'precio']

class CargoCotizacionPostSerializer(serializers.ModelSerializer):
    solicitud = serializers.PrimaryKeyRelatedField(queryset = SolicitudCotizacion.objects.all())
    class Meta:
        model = CargoExtraCotizacion
        fields = '__all__'

class MobiliarioPorCotizarListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        mobiliario_mapping = {mobiliario.id: mobiliario for mobiliario in instance}
        data_mapping = {item['id']: item for item in validated_data}

        ret = []
        for mobiliario_id, data in data_mapping.items():
            mobiliario = mobiliario_mapping.get(mobiliario_id, None)
            if not mobiliario is None:
                ret.append(self.child.update(mobiliario, data))
        return ret
    
class MobiliarioPorCotizarPutListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = MobiliarioPorCotizar
        fields = '__all__'
        list_serializer_class = MobiliarioPorCotizarListSerializer

class MobiliarioPorPedirSerializer(serializers.ModelSerializer):
    mobiliario = MobiliarioOnGetSerializer()
    disponibilidad = serializers.SerializerMethodField()
    class Meta:
        model = MobiliarioPorCotizar
        fields = ['mobiliario', 'cantidad', 'precio', 'id', 'disponibilidad']

    def get_disponibilidad(self, obj):
        mob = obj.mobiliario
        mob_disponible = mobiliarioDisponibleEnPeriodo(mob, obj.solicitud.fechaEntrega, obj.solicitud.fechaRecoleccion)
        return mob_disponible

class PedidoClienteSerializer(serializers.ModelSerializer):
    mype = MypeShortSerializer()
    class Meta:
        model = Pedido
        fields = ['mype', 'fechaEntrega', 'fechaRecoleccion', 'estado', 'id']

class ComentarioFullSerializer(serializers.ModelSerializer):
    pedido = serializers.PrimaryKeyRelatedField(queryset=Pedido.objects.all())
    mype = serializers.PrimaryKeyRelatedField(queryset=Mype.objects.all())
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    class Meta:
        model = Comentario
        fields = '__all__'

class MobiliarioDisponibleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fechaInicio = serializers.DateTimeField()
    fechaFin = serializers.DateTimeField()