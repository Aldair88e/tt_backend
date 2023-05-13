from django.shortcuts import render, get_object_or_404
from usuarios.models import ClientePorTelefono, Usuario, Cliente, Direccion
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import views
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .serializers import CrearClienteSerializer, ModificarClienteSerializer, PutClienteporTelSerializer, GetClienteSerializer, ClienteParaListaSerializer, ClienteShortSerializer
from usuarios.serializers import DireccionPutSerializer
from django.http import JsonResponse, Http404
from rest_framework.renderers import JSONRenderer
from django.db.models import Sum, Count, FloatField, Subquery, OuterRef, IntegerField, F
from GestionInventario.serializers import MobiliarioPerdidoPorClienteSerializer
from gestionPedidos.serializers import PedidoParaHistorialClienteSerializer
# from usuarios.serializers import RegistroClienteSerializer
# Create your views here.

class ClientePorTelefonoView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    USUARIONOMYPE = {
        "resultado": "El usuario no es de tipo MYPE",
    }
    NOT_FOUND = {
        'error': 'El registro no se encontró en la base de datos',
    }

    def post(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        if user.is_mype:
            mype = user.mype
            data = JSONParser().parse(request)
            serializer = CrearClienteSerializer(data=data)
            if serializer.is_valid():
                clienteData = serializer.validated_data['cliente']
                direccionData = serializer.validated_data['direccion']
                descuento = serializer.validated_data['descuento']
                cliente = Cliente.objects.create(**clienteData)
                direccion = Direccion.objects.create(**direccionData)
                cliente.direcciones.add(direccion)
                clienteTelefono = ClientePorTelefono.objects.create(descuento=descuento, cliente=cliente, mype=mype)
                response = {
                    "mensaje": "El cliente se agregó correctamente",
                }
                return Response(response, status = 200)
            return JsonResponse(serializer.errors, status = 400)
        return  Response(self.USUARIONOMYPE, status = 403)
    
    def put(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        if user.is_mype:
            mype = user.mype
            data = JSONParser().parse(request)
            serializer = ModificarClienteSerializer(data=data, partial = True) 
            if serializer.is_valid():
                cliente_data = serializer.validated_data.pop('cliente')
                direcciones_data = serializer.validated_data.pop('direcciones')
                descuento = serializer.validated_data.pop('descuento')
                instancias = mype.clienteportelefono_set.filter(pk=cliente_data['id'])
                if instancias.exists():
                    direcciones = []
                    for i in instancias:
                        cliente = i.cliente
                        i.descuento = descuento
                        cliente.nombre = cliente_data['nombre']
                        cliente.apellido1 = cliente_data['apellido1']
                        cliente.apellido2 = cliente_data['apellido2']
                        cliente.telefono = cliente_data['telefono']
                        cliente.save()
                        i.save()
                        direcciones = cliente.direcciones.all()
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
                    
                    response = {
                        "resultado": "la operación se realizó exitosamente",
                    }
                    return Response(response, status=200) 
                response = {
                        "resultado": "No se encontró el registro en la base de datos",
                }
                return Response(response, status=404)           
            return JsonResponse(serializer.errors, status=400)
        response = {
            'usuario' : 'El usuario no es de tipo MYPE',
        }
        return  Response(response, status = 400)
    
    def delete(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        if user.is_mype:
            mype = user.mype
            data = JSONParser().parse(request)
            serializer = PutClienteporTelSerializer(data=data, partial = True)
            if serializer.is_valid():
                clientePorTel = mype.clienteportelefono_set.filter(pk=serializer.validated_data['id'])
                if clientePorTel.exists():
                    for c in clientePorTel:
                        cliente = c.cliente
                        if not cliente.is_web: 
                            direcciones = cliente.direcciones.all()
                            for d in direcciones:
                                d.delete()
                            c.delete()
                            cliente.delete()
                            response = {
                                "resultado" : "Los datos del cliente se eliminaron correctamente",
                            }
                            return Response(response, status=200)
                        response = {
                            "resultado" : "No tienes permisos para eliminar este registro",
                        }
                        return Response(response, status=403)
                response = {
                    "resultado" : "No se pudo encontrar el registro",
                }
                return Response(response, status=404)
            return JsonResponse(serializer.errors, status=400)
        response = {
            'usuario' : 'El usuario no es de tipo MYPE',
        }
        return  Response(response, status = 400)
    
    def get(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        if user.is_mype:
            mype = user.mype
            cliente_id = request.headers['Cliente-Id']
            cliente = get_object_or_404(Cliente, id=cliente_id)
            if cliente.is_web:
                response = {
                    "resultado": "el cliente es web",
                }
                return Response(response, 200)
            clientePorTel = mype.clienteportelefono_set.filter(pk=cliente_id)
            if clientePorTel.exists():
                for cpt in clientePorTel:
                    clienteInst = cpt.cliente
                    mobiliarioPerdido = clienteInst.mobiliarioperdido_set.all()
                    precio_mobiliario_sum =clienteInst.pedido_set.annotate(total_mobiliario = Sum(F('mobiliariorentado__precio')*F('mobiliariorentado__cantidad'))).filter(pk=OuterRef('pk'))
                    cargos_sum = clienteInst.pedido_set.annotate(total_cargos = Sum('cargoextra__precio')).filter(pk=OuterRef('pk'))
                    pedidos = clienteInst.pedido_set.annotate(
                        total_mobiliario = Subquery(precio_mobiliario_sum.values('total_mobiliario'), output_field=FloatField()),
                        total_cargos = Subquery(cargos_sum.values('total_cargos'), output_field=FloatField())
                    )
                    serializerCliente = GetClienteSerializer(clienteInst)
                    serializerMobPerdido = MobiliarioPerdidoPorClienteSerializer(mobiliarioPerdido, many=True)
                    serializerPedido = PedidoParaHistorialClienteSerializer(pedidos, many=True)
                    response = {
                        "cliente" : JSONRenderer().render(serializerCliente.data),
                        "mobPerdido" : JSONRenderer().render(serializerMobPerdido.data),
                        "pedidos" : JSONRenderer().render(serializerPedido.data),
                    }
                    return Response(response, status=200)
            return Response(self.NOT_FOUND, status=404)
            # return JsonResponse(serializer.errors, status=400)
        return  Response(self.USUARIONOMYPE, status = 403)
    
class ListaClientesView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    USUARIONOMYPE = {
        "resultado": "El usuario no es de tipo MYPE",
    }
    NOT_FOUND = {
        'error': 'El registro no se encontró en la base de datos',
    }

    def get(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        if user.is_mype:
            mype = user.mype
            clientesPorTel = mype.clienteportelefono_set.all()
            mobiliarioPerdidoInfo = Cliente.objects.annotate(
                mobiliario_perdido = Sum('mobiliarioperdido__cantidad'),
                mobPerdido_adeudo = Sum('mobiliarioperdido__totalReposicion'),
                mobPerdido_pagado = Sum('mobiliarioperdido__pagoRecibido')
            ).filter(pk=OuterRef('pk'))
            pedidoInfo = Cliente.objects.annotate(
                total_pedidos = Count('pedido')
            ).filter(pk=OuterRef('pk'))
            # clientesQS = Cliente.objects.annotate(
            #     mobiliario_perdido=Sum('mobiliarioperdido__cantidad')
            #     ).annotate(
            #     mobPerdido_adeudo = Sum('mobiliarioperdido__totalReposicion')
            #     ).annotate(
            #     mobPerdido_pagado = Sum('mobiliarioperdido__pagoRecibido')
            #     ).annotate(
            #     descuento = Sum('clienteportelefono__descuento')
            #     )
            clientesQS = Cliente.objects.annotate(
                mobiliario_perdido=Subquery(mobiliarioPerdidoInfo.values('mobiliario_perdido'), output_field = IntegerField()),
                mobPerdido_adeudo = Subquery(mobiliarioPerdidoInfo.values('mobPerdido_adeudo'), output_field = FloatField()),
                mobPerdido_pagado = Subquery(mobiliarioPerdidoInfo.values('mobPerdido_pagado'), output_field = FloatField()),
                total_pedidos = Subquery(pedidoInfo.values('total_pedidos'), output_field = IntegerField()),
                )
            clientesMype = clientesQS.filter(id__in=clientesPorTel).prefetch_related('direcciones')
            serializer = ClienteParaListaSerializer(clientesMype, many=True)
            jsonData = JSONRenderer().render(serializer.data)
            return Response(jsonData, status=200)
        return  Response(self.USUARIONOMYPE, status = 403)
    
class ClientesShortView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    USUARIONOMYPE = {
        "resultado": "El usuario no es de tipo MYPE",
    }
    def get(self, request):
        user = get_object_or_404(Usuario, username=self.request.user)
        if user.is_mype:
            mype = user.mype
            clientesPorTel = mype.clienteportelefono_set.all()
            clientesQS = Cliente.objects.all()
            clientesMype = clientesQS.filter(id__in=clientesPorTel)
            serializer = ClienteShortSerializer(clientesMype, many=True)
            jsonData = JSONRenderer().render(serializer.data)
            return Response(jsonData, status=200)
        return  Response(self.USUARIONOMYPE, status = 403)