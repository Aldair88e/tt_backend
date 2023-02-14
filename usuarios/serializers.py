from django.db import transaction
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import Cliente, Usuario, Direccion, Mype

class CustomRegisterSerializer(RegisterSerializer):
    is_mype = serializers.BooleanField()

    @transaction.atomic
    def save(self, request):
        usuario = super().save(request)
        usuario.is_mype = self.data.get('is_mype')
        usuario.save()
        return usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'is_mype', 'have_data']
        read_only_fields = ['id', 'is_mype']


class ClienteSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(many = False, queryset = Usuario.objects.all())
    class Meta:
        model = Cliente
        exclude = ['direcciones']

class ClientePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        exclude = ['direcciones', 'usuario']
        
class DireccionPutSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Direccion
        fields = '__all__'

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = '__all__'

class RegistroClienteSerializer(serializers.Serializer):
    cliente = ClienteSerializer()
    direccion = DireccionSerializer()

class UpdateClienteSerializer(serializers.Serializer):
    cliente = ClientePutSerializer()
    direcciones = DireccionPutSerializer(many=True)
    
class MypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mype
        exclude = ['direcciones', 'usuario']

class RegistroMypeSerializer(serializers.Serializer):
    mype = MypeSerializer()
    direccion = DireccionSerializer()

class PutMypeSerializer(serializers.Serializer):
    mype = MypeSerializer()
    direcciones = DireccionPutSerializer(many=True)