from django.db import transaction
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import PasswordResetSerializer
from .models import Cliente, Usuario, Direccion, Mype
from .forms import CustomAllAuthPasswordResetForm

class CustomRegisterSerializer(RegisterSerializer):
    is_mype = serializers.BooleanField()

    @transaction.atomic
    def save(self, request):
        usuario = super().save(request)
        usuario.is_mype = self.data.get('is_mype')
        usuario.save()
        return usuario
    
class MyPasswordResetSerializer(PasswordResetSerializer):
    def validate_email(self, value):
        # use the custom reset form
        self.reset_form = CustomAllAuthPasswordResetForm(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'is_mype', 'have_data']
        read_only_fields = ['id', 'is_mype']


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        exclude = ['direcciones']


class ClientePutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        exclude = ['direcciones']
        
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
    cliente = ClientePutSerializer()
    direccion = DireccionSerializer()

class UpdateClienteSerializer(serializers.Serializer):
    cliente = ClientePutSerializer()
    direcciones = DireccionPutSerializer(many=True)
    
class MypeSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(max_length=None, use_url=True)
    class Meta:
        model = Mype
        exclude = ['direcciones', 'usuario']

class RegistroMypeSerializer(serializers.Serializer):
    mype = MypeSerializer()
    direccion = DireccionSerializer()

class PutMypeSerializer(serializers.Serializer):
    mype = MypeSerializer()
    direcciones = DireccionPutSerializer(many=True)

class getMypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mype
        fields = ['nombreEmpresa']

class getClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['nombre']
