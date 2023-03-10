from django.shortcuts import render
from rest_framework import views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Usuario, Cliente, Direccion, Mype
from django.shortcuts import get_object_or_404
from .serializers import UsuarioSerializer, RegistroClienteSerializer, DireccionSerializer, UpdateClienteSerializer, RegistroMypeSerializer, ClientePutSerializer, DireccionPutSerializer, MypeSerializer, PutMypeSerializer, getClienteSerializer, getMypeSerializer
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
# Create your views here.
class user_haveData(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        serializer = UsuarioSerializer(user)
        if user.is_mype and user.have_data:
            mype =user.mype
            # serializerMype = getMypeSerializer(mype)
            # print(serializerMype.data)
            response = {
                "id": user.id, 
                "is_mype" : user.is_mype,
                "have_data" : user.have_data,
                "nombre" : mype.nombreEmpresa
            }
            return Response(response)
        elif user.have_data and not(user.is_mype):
            cliente = user.cliente
            # serializerCliente = getClienteSerializer(cliente)
            # print(serializerCliente.data)
            response = {
                "id": user.id, 
                "is_mype" : user.is_mype,
                "have_data" : user.have_data,
                "nombre" : cliente.nombre
            }
            return Response(response)
        print(serializer.data)
        return Response(serializer.data)

class clienteRegistro(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = JSONParser().parse(request)
        user = get_object_or_404(Usuario, username=self.request.user)
        serializer = RegistroClienteSerializer(data=data)
        if serializer.is_valid():
            cliente_data = serializer.validated_data['cliente']
            direccion_data = serializer.validated_data['direccion']
            cli = Cliente.objects.create(usuario=user, **cliente_data)
            direccion = Direccion.objects.create(**direccion_data)
            cli.direcciones.add(direccion)
            print(cli)
            print(direccion)
            usuario = cli.usuario
            usuario.have_data = True
            usuario.save()
            userSerializer = UsuarioSerializer(usuario)
            return JsonResponse(userSerializer.data, status=201)
        print(serializer.errors)
        return JsonResponse(serializer.errors, status=400)

    def get(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        cliente = user.cliente
        direcciones = cliente.direcciones.all()
        serializerCliente = ClientePutSerializer(cliente)
        serializerDireccion = DireccionSerializer(direcciones, many=True)
        response = {
            "cliente" : JSONRenderer().render(serializerCliente.data),
            "direcciones": JSONRenderer().render(serializerDireccion.data)
        }
        return Response(response)
    
    def put(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        cliente = user.cliente
        direcciones = cliente.direcciones.all()
        data = JSONParser().parse(request)
        serializer = UpdateClienteSerializer(data=data, partial = True)
        
        if serializer.is_valid():
            print(serializer.data)
            cliente_data = serializer.validated_data.pop('cliente')
            print(cliente_data)
            direcciones_data = serializer.validated_data.pop('direcciones')
            print(direcciones_data)
            serializer_cliente = ClientePutSerializer(cliente, cliente_data, partial=True)
            if serializer_cliente.is_valid():
                serializer_cliente.save()
                dir = []
                for direccion in direcciones_data:
                    id = direccion['id']
                    for direc in direcciones:
                        if id == direc.id:
                            dir.append(DireccionPutSerializer(direc, direccion, partial=True))
                for d in dir:
                    if d.is_valid():
                        d.save()
                    else:    
                        return JsonResponse(d.errors, status=400)
                response={
                    "Resultado": "La operacion fue exitosa"
                }
                return Response(response)
            return JsonResponse(serializer_cliente.errors, status=400)

class MypeRegistro(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        if user.is_mype:
            data = JSONParser().parse(request)
            serializer = RegistroMypeSerializer(data=data)
            if serializer.is_valid():
                mype_data = serializer.validated_data['mype']
                direccion_data = serializer.validated_data['direccion']
                mype = Mype.objects.create(usuario=user, **mype_data)
                direccion = Direccion.objects.create(**direccion_data)
                mype.direcciones.add(direccion)
                print(mype)
                print(direccion)
                user.have_data = True
                user.save()
                userSerializer = UsuarioSerializer(user)
                return JsonResponse(userSerializer.data, status=201)
            return JsonResponse(serializer.errors, status=400)
        response = {
            "Error" : "El usuario no es de tipo MYPE",
        }
        return Response(response, status=400)
    
    def get(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        if user.is_mype:
            mype = user.mype
            direcciones = mype.direcciones.all()
            serializerMype = MypeSerializer(mype)
            serializerDireccion = DireccionSerializer(direcciones, many=True)
            response = {
                "mype" : JSONRenderer().render(serializerMype.data),
                "direcciones": JSONRenderer().render(serializerDireccion.data)
            }
            return Response(response)
        response = {
            "Error": "El usuario no es de tipo MYPE",
        }
        return Response(response, status=400)

    def put(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        if user.is_mype:
            mype = user.mype
            direcciones = mype.direcciones.all()
            data = JSONParser().parse(request)
            serializer = PutMypeSerializer(data=data, partial = True)
            if serializer.is_valid():
                print(serializer.data)
                mype_data = serializer.validated_data.pop('mype')
                print(mype_data)
                direcciones_data = serializer.validated_data.pop('direcciones')
                print(direcciones_data)
                serializer_mype = MypeSerializer(mype, mype_data, partial=True)
                if serializer_mype.is_valid():
                    serializer_mype.save()
                    dir = []
                    for direccion in direcciones_data:
                        id = direccion['id']
                        for direc in direcciones:
                            if id == direc.id:
                                dir.append(DireccionPutSerializer(direc, direccion, partial=True))
                    for d in dir:
                        if d.is_valid():
                            d.save()
                        else:    
                            return JsonResponse(d.errors, status=400)
                    response={
                        "Resultado": "La operacion fue exitosa"
                    }
                    return Response(response)
                return JsonResponse(serializer_mype.errors, status=400)
        response = {
            "Error": "El usuario no es de tipo MYPE",
        }
        return Response(response, status=400)