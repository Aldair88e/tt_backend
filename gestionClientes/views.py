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
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from busquedaCotizacion.forms import IdMypeForm
from django.template.loader import render_to_string
from datetime import datetime
import pytz
from headless_pdfkit import generate_pdf
from GestionInventario.constantes import NO_MYPE_RESPONSE, NO_SE_ENCOTRO, TOTAL_INSUFICIENTE, OPERACION_EXITOSA
from django.http import Http404, HttpResponse
from django.db.models.functions import Coalesce
from gestionPedidos.models import Pedido
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
                cliente = Cliente.objects.create(**clienteData)
                direccion = Direccion.objects.create(**direccionData)
                cliente.direcciones.add(direccion)
                clienteTelefono = ClientePorTelefono.objects.create(cliente=cliente, mype=mype)
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
                instancias = mype.clienteportelefono_set.filter(pk=cliente_data['id'])
                if instancias.exists():
                    direcciones = []
                    for i in instancias:
                        cliente = i.cliente
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
                else:
                    cliente = get_object_or_404(Cliente, pk=serializer.validated_data['id'])
                    pedidos = mype.pedido_set.filter(cliente_id = cliente.id)
                    for p in pedidos:
                        p.delete()
                    response = {
                        "resultado" : "Los datos del cliente se eliminaron correctamente",
                    }
                    return Response(response, status=200)
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
                mobiliarioPerdido = cliente.mobiliarioperdido_set.all()
                precio_mobiliario_sum =cliente.pedido_set.annotate(total_mobiliario = Sum(F('mobiliariorentado__precio')*F('mobiliariorentado__cantidad'))).filter(pk=OuterRef('pk'))
                cargos_sum = cliente.pedido_set.annotate(total_cargos = Sum('cargoextra__precio')).filter(pk=OuterRef('pk'))
                pedidos = cliente.pedido_set.annotate(
                    total_mobiliario = Subquery(precio_mobiliario_sum.values('total_mobiliario'), output_field=FloatField()),
                    total_cargos = Subquery(cargos_sum.values('total_cargos'), output_field=FloatField())
                )
                serializerCliente = GetClienteSerializer(cliente)
                serializerMobPerdido = MobiliarioPerdidoPorClienteSerializer(mobiliarioPerdido, many=True)
                serializerPedido = PedidoParaHistorialClienteSerializer(pedidos, many=True)
                response = {
                    "cliente" : JSONRenderer().render(serializerCliente.data),
                    "mobPerdido" : JSONRenderer().render(serializerMobPerdido.data),
                    "pedidos" : JSONRenderer().render(serializerPedido.data),
                }
                return Response(response, status=200)
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
            pedidosQS1 = Pedido.objects.filter(pk = OuterRef('pedido__id')).annotate(
                adeudo_pedido = Coalesce(Sum(F('mobiliariorentado__precio') * F('mobiliariorentado__cantidad')), 0, output_field=FloatField())
            ).values('adeudo_pedido')
            pedidosQS2 = Pedido.objects.filter(pk = OuterRef('pedido__id')).annotate(
                adeudo_cargos = Coalesce(Sum('cargoextra__precio'), 0, output_field=FloatField())
            ).values('adeudo_cargos')

            pedidosQS3 = Cliente.objects.filter(pk = OuterRef('pk')).annotate(pedidos_cobrado = Coalesce(Sum('pedido__pagoRecibido'), 0, output_field=FloatField())).values('pedidos_cobrado')
     
            mobiliario_perdido_cantidad = Cliente.objects.annotate(
            mobiliario_perdido = Sum('mobiliarioperdido__cantidad', output_field=IntegerField())).filter(pk=OuterRef('pk'))

            mobPerdido_adeudo_qs = Cliente.objects.filter(pk=OuterRef('pk')).annotate(
                mobPerdido_adeudo = Coalesce(Sum('mobiliarioperdido__totalReposicion'), 0, output_field=FloatField()) - Coalesce(Sum('mobiliarioperdido__pagoRecibido'), 0,output_field=FloatField())
                )

            pedidoInfo = Cliente.objects.filter(pk=OuterRef('pk')).annotate(
                total_pedidos = Count('pedido', output_field=IntegerField())
            )

            clientesQS = Cliente.objects.annotate(
                mobiliario_perdido=Coalesce(Subquery(mobiliario_perdido_cantidad.values('mobiliario_perdido')[:1], output_field = IntegerField()), 0, output_field=IntegerField()),
                mobPerdido_adeudo = Subquery(mobPerdido_adeudo_qs.values('mobPerdido_adeudo')[:1], output_field = FloatField()),
                total_pedidos = Subquery(pedidoInfo.values('total_pedidos')[:1], output_field = IntegerField()),
                adeudos_pedido=Coalesce(Sum(Subquery(pedidosQS1, output_field=FloatField())), 0, output_field=FloatField()),
                adeudos_cargos = Coalesce(Sum(Subquery(pedidosQS2, output_field=FloatField())), 0, output_field=FloatField()),
                pagos_recibidos = Coalesce(Subquery(pedidosQS3, output_field=FloatField()), 0, output_field=FloatField())
                ).annotate(
                    adeudo = F('mobPerdido_adeudo') + F('adeudos_pedido') + F('adeudos_cargos') - F('pagos_recibidos')
                )
            
            pedidos = mype.pedido_set.all().values_list('cliente_id', flat=True)
            clientesTel = mype.clienteportelefono_set.exclude(pk__in=pedidos).values_list('pk', flat=True)
            clientesMype = clientesQS.filter(id__in=pedidos).prefetch_related('direcciones')
            clientesTel = clientesQS.filter(id__in=clientesTel).prefetch_related('direcciones')
            clientesTotal = clientesMype | clientesTel
            serializer = ClienteParaListaSerializer(clientesTotal, many=True)
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
    
@api_view(('GET',))
@authentication_classes([])
@permission_classes([])
@renderer_classes((JSONRenderer,))
def getListaClientesPDF(request, userId):
    idForm = IdMypeForm({"id":userId})
    if idForm.is_valid():
        user = get_object_or_404(Usuario, pk= userId)
        if user.is_mype: 
            Tz = pytz.timezone("America/Mexico_City")
            hoy = datetime.now(Tz).date()
            mypeObject = user.mype

            pedidosQS1 = Pedido.objects.filter(pk = OuterRef('pedido__id')).annotate(
                adeudo_pedido = Coalesce(Sum(F('mobiliariorentado__precio') * F('mobiliariorentado__cantidad')), 0, output_field=FloatField())
            ).values('adeudo_pedido')
            pedidosQS2 = Pedido.objects.filter(pk = OuterRef('pedido__id')).annotate(
                adeudo_cargos = Coalesce(Sum('cargoextra__precio'), 0, output_field=FloatField())
            ).values('adeudo_cargos')

            pedidosQS3 = Cliente.objects.filter(pk = OuterRef('pk')).annotate(pedidos_cobrado = Coalesce(Sum('pedido__pagoRecibido'), 0, output_field=FloatField())).values('pedidos_cobrado')
     
            mobiliario_perdido_cantidad = Cliente.objects.annotate(
            mobiliario_perdido = Sum('mobiliarioperdido__cantidad', output_field=IntegerField())).filter(pk=OuterRef('pk'))

            mobPerdido_adeudo_qs = Cliente.objects.filter(pk=OuterRef('pk')).annotate(
                mobPerdido_adeudo = Coalesce(Sum('mobiliarioperdido__totalReposicion'), 0, output_field=FloatField()) - Coalesce(Sum('mobiliarioperdido__pagoRecibido'), 0,output_field=FloatField())
                )

            pedidoInfo = Cliente.objects.filter(pk=OuterRef('pk')).annotate(
                total_pedidos = Count('pedido', output_field=IntegerField())
            )

            clientesQS = Cliente.objects.annotate(
                mobiliario_perdido=Coalesce(Subquery(mobiliario_perdido_cantidad.values('mobiliario_perdido')[:1], output_field = IntegerField()), 0, output_field=IntegerField()),
                mobPerdido_adeudo = Subquery(mobPerdido_adeudo_qs.values('mobPerdido_adeudo')[:1], output_field = FloatField()),
                total_pedidos = Subquery(pedidoInfo.values('total_pedidos')[:1], output_field = IntegerField()),
                adeudos_pedido=Coalesce(Sum(Subquery(pedidosQS1, output_field=FloatField())), 0, output_field=FloatField()),
                adeudos_cargos = Coalesce(Sum(Subquery(pedidosQS2, output_field=FloatField())), 0, output_field=FloatField()),
                pagos_recibidos = Coalesce(Subquery(pedidosQS3, output_field=FloatField()), 0, output_field=FloatField())
                ).annotate(
                    adeudo = F('mobPerdido_adeudo') + F('adeudos_pedido') + F('adeudos_cargos') - F('pagos_recibidos')
                )
            
            pedidos = mypeObject.pedido_set.all().values_list('cliente_id', flat=True)
            clientesTel = mypeObject.clienteportelefono_set.exclude(pk__in=pedidos).values_list('pk', flat=True)
            clientesMype = clientesQS.filter(id__in=pedidos).prefetch_related('direcciones')
            clientesTel = clientesQS.filter(id__in=clientesTel).prefetch_related('direcciones')
            clientesTotal = clientesMype | clientesTel
            direccionMype = mypeObject.direcciones.all()
            context = {
                'clientes': clientesTotal,
                'empresa': mypeObject,
                'direccionMype': direccionMype,
                'fecha': hoy,
            }
            html = render_to_string("listaClientes.html", context)
            options = {
                'page-size': 'Letter',
                'orientation': 'Landscape',
            }
            pdf = generate_pdf(html, options = options)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="listaClientes_{}.pdf"'.format(mypeObject.nombreEmpresa)
            return response
        return Response(NO_MYPE_RESPONSE, status=403)
    errorResponse = '<!doctype html><html><head><title>Error</title></head><body>'+idForm.errors+'</body></html>'
    return HttpResponse(errorResponse, status=400)

@api_view(('GET',))
@authentication_classes([])
@permission_classes([])
@renderer_classes((JSONRenderer,))
def getClientePDF(request, userId, clienteId):
    idForm = IdMypeForm({"id":userId})
    if idForm.is_valid():
        user = get_object_or_404(Usuario, pk= userId)
        if user.is_mype: 
            mypeObject = user.mype
            cliente = get_object_or_404(Cliente, id=clienteId)
            mobiliarioPerdido = cliente.mobiliarioperdido_set.all().annotate(
                adeudo = Coalesce(F('totalReposicion'), 0, output_field=FloatField()) - Coalesce(F('pagoRecibido'), 0, output_field=FloatField())
            )
            precio_mobiliario_sum =cliente.pedido_set.annotate(total_mobiliario = Sum(F('mobiliariorentado__precio')*F('mobiliariorentado__cantidad'))).filter(pk=OuterRef('pk'))
            cargos_sum = cliente.pedido_set.annotate(total_cargos = Sum('cargoextra__precio')).filter(pk=OuterRef('pk'))
            pedidos = cliente.pedido_set.annotate(
                total_mobiliario = Coalesce(Subquery(precio_mobiliario_sum.values('total_mobiliario')), 0, output_field=FloatField()),
                total_cargos = Coalesce(Subquery(cargos_sum.values('total_cargos')), 0, output_field=FloatField())
            ).annotate(
                adeudo = F('total_mobiliario') + F('total_cargos') - F('pagoRecibido')
            ).annotate(
                total = F('total_mobiliario') + F('total_cargos')
            )
           
            direccionMype = mypeObject.direcciones.all()
            context = {
                'cliente': cliente,
                'empresa': mypeObject,
                'direccionMype': direccionMype,
                'mobiliarioPerdido': mobiliarioPerdido,
                'pedidos': pedidos,
            }
            html = render_to_string("cliente.html", context)
            options = {
                'page-size': 'Letter',
                'orientation': 'Landscape',
            }
            pdf = generate_pdf(html, options = options)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="lientes_{}_{}.pdf"'.format(cliente.id, mypeObject.nombreEmpresa)
            return response
        return Response(NO_MYPE_RESPONSE, status=403)
    errorResponse = '<!doctype html><html><head><title>Error</title></head><body>'+idForm.errors+'</body></html>'
    return HttpResponse(errorResponse, status=400)