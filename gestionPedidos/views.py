from django.conf import settings
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from usuarios.models import Usuario, Cliente
from .models import CargoExtra, Pedido
from .serializers import CargoExtraSerializer, PedidoRegistroSerializer, PedidoSerializerOnPut, PedidoGetSerializer, PedidoParaListaSerializer, CargoExtraPostSerializer, PedidoParaClienteSerializer
from django.http import JsonResponse, HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.db.models import Sum, FloatField, Subquery, OuterRef, Case, When
from GestionInventario.constantes import NO_MYPE_RESPONSE, OPERACION_EXITOSA
from GestionInventario.models import MobiliarioRentado, Mobiliario
from django.http import Http404
from .funciones import mobiliarioDisponibleEnPeriodo
from GestionInventario.serializers import GetMobiliarioRentadoSerializer, MobiliarioRentadoClienteSerializer
from django.db.models import F
from django.template.loader import render_to_string
from datetime import timedelta, datetime
import pytz
import os
from headless_pdfkit import generate_pdf
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from busquedaCotizacion.forms import IdMypeForm




# Create your views here.
class CargoExtraView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            data = JSONParser().parse(request)
            serializer = CargoExtraPostSerializer(data=data)
            if serializer.is_valid():
                pedido_id = serializer.validated_data['pedido']
                pedido = get_object_or_404(Pedido, id = pedido_id)
                nuevoCargo = CargoExtra.objects.create(pedido = pedido, concepto = serializer.validated_data['concepto'], precio = serializer.validated_data['precio'])
                return Response(OPERACION_EXITOSA, status=200)
            return JsonResponse(serializer.errors, status=400)   
        return Response(NO_MYPE_RESPONSE, status=403)

    def put(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            data = JSONParser().parse(request)
            serializer = CargoExtraSerializer(data=data)
            if serializer.is_valid():
                idCargo = serializer.validated_data['id']
                cargo = get_object_or_404(CargoExtra, id=idCargo)
                cargo.concepto = serializer.validated_data['concepto']
                cargo.precio = serializer.validated_data['precio']
                cargo.save()
                return Response(OPERACION_EXITOSA, status=200)
            return JsonResponse(serializer.errors, status=400)
        return Response(NO_MYPE_RESPONSE, status=403)
    
    def delete(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            data = JSONParser().parse(request)
            serializer = CargoExtraSerializer(data=data, partial=True)
            if serializer.is_valid():
                idCargo = serializer.validated_data['id']
                cargo = get_object_or_404(CargoExtra, id=idCargo)
                cargo.delete()
                return Response(OPERACION_EXITOSA, status=200)
            return JsonResponse(serializer.errors, status=400)
        return Response(NO_MYPE_RESPONSE, status=403)
    
class PedidoView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def validarCantidad(self, id_mobiliario, fechaInicio, fechaFin, nuevaCantidad, viejaCantidad=0, ):
        mobiliario = get_object_or_404(Mobiliario, id = id_mobiliario)
        disponible = mobiliarioDisponibleEnPeriodo(id_mobiliario, fechaInicio, fechaFin)
        if (disponible - nuevaCantidad + viejaCantidad) < 0:
            return mobiliario.nombre
        return ''
    
    def evaluarNuevasFechas(self, pedido, FechaIni, FechaFin):
        errores = ''
        mobiliarioRentado = pedido.mobiliariorentado_set.select_related('mobiliario')
        if(FechaIni == pedido.fechaEntrega and FechaFin== pedido.fechaRecoleccion):
            return 0;
        if(FechaIni<pedido.fechaEntrega):
            if(FechaFin == pedido.fechaRecoleccion):
                for mob in mobiliarioRentado:
                    disponible = mobiliarioDisponibleEnPeriodo(mob.mobiliario.id, FechaIni, pedido.fechaEntrega)
                    if(disponible-mob.cantidad)<0:
                        errores = errores + ',' + mob.mobiliario.nombre
                return errores
            if(FechaFin <= pedido.fechaEntrega):
                for mob in mobiliarioRentado:
                    disponible = mobiliarioDisponibleEnPeriodo(mob.mobiliario.id, FechaIni, FechaFin)
                    if(disponible-mob.cantidad)<0:
                        errores = errores + ',' + mob.mobiliario.nombre
                return errores
            if(FechaFin>pedido.fechaEntrega and FechaFin < pedido.fechaRecoleccion):
                for mob in mobiliarioRentado:
                    disponible = mobiliarioDisponibleEnPeriodo(mob.mobiliario.id, FechaIni, pedido.fechaEntrega)
                    if(disponible-mob.cantidad)<0:
                        errores = errores + ',' + mob.mobiliario.nombre
                return errores
            if(FechaFin > pedido.fechaRecoleccion):
                for mob in mobiliarioRentado:
                    disponible = mobiliarioDisponibleEnPeriodo(mob.mobiliario.id, FechaIni, pedido.fechaEntrega)
                    disponible2 = mobiliarioDisponibleEnPeriodo(mob.mobiliario.id, pedido.fechaRecoleccion, FechaFin)
                    if((disponible-mob.cantidad) or (disponible2 - mob.cantidad))<0:
                        errores = errores + ',' + mob.mobiliario.nombre
                return errores
        if(FechaIni == pedido.fechaEntrega):
            if(FechaFin<pedido.fechaRecoleccion):
                return errores
            if(FechaFin>pedido.fechaRecoleccion):
                for mob in mobiliarioRentado:
                    disponible = mobiliarioDisponibleEnPeriodo(mob.mobiliario.id, pedido.fechaEntrega, FechaFin)
                    if(disponible-mob.cantidad)<0:
                        errores = errores + ',' + mob.mobiliario.nombre
                return errores
        if(FechaIni>pedido.fechaEntrega and FechaIni<pedido.fechaRecoleccion):
            if(FechaFin == pedido.fechaRecoleccion):
                return errores
            if(FechaFin < pedido.fechaRecoleccion):
                return errores
            if(FechaFin>pedido.fechaRecoleccion):
                for mob in mobiliarioRentado:
                    disponible = mobiliarioDisponibleEnPeriodo(mob.mobiliario.id, pedido.fechaRecoleccion, FechaFin)
                    if(disponible-mob.cantidad)<0:
                        errores = errores + ',' + mob.mobiliario.nombre
                return errores
        if(FechaIni>pedido.fechaRecoleccion):
            for mob in mobiliarioRentado:
                disponible = mobiliarioDisponibleEnPeriodo(mob.mobiliario.id, FechaIni, FechaFin)
                if(disponible-mob.cantidad)<0:
                    errores = errores + ',' + mob.mobiliario.nombre
            return errores
        
    def post(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            mype = user.mype
            data = JSONParser().parse(request)
            serializer = PedidoRegistroSerializer(data=data) 
            if serializer.is_valid():
                id_cliente = serializer.validated_data['cliente']
                datosPedido = serializer.validated_data['pedido']
                cliente = get_object_or_404(Cliente, id=id_cliente)
                pedido = Pedido.objects.create(mype= mype, cliente=cliente, **datosPedido)
                mobiliarioRentado = serializer.validated_data['mobiliarioRentado']
                erroresEnMobRentado = []
                for m in mobiliarioRentado:
                    id_mobiliario = m['id']
                    print(id_mobiliario)
                    mobiliario = get_object_or_404(Mobiliario, id=id_mobiliario)
                    print(mobiliario)
                    error = self.validarCantidad(id_mobiliario, pedido.fechaEntrega, pedido.fechaRecoleccion, m['cantidad'])
                    if not error:   
                        mobCreado = MobiliarioRentado.objects.create(mobiliario = mobiliario, pedido=pedido, precio=m['precio'], cantidad = m['cantidad'])
                    else:
                        erroresEnMobRentado.append(error)    
                cargosExtra = serializer.validated_data['cargosExtra']
                for c in cargosExtra:
                    CargoExtra.objects.create(pedido=pedido, **c)
                
                errores = ""
                for e in erroresEnMobRentado:
                    errores = errores + "," + e;
                response = {
                    "id": pedido.id,
                    "errores": errores,
                }
                return Response(response, 200)
            return JsonResponse(serializer.errors, status=400)
        return Response(NO_MYPE_RESPONSE, status=403)
    
    def put(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            data = JSONParser().parse(request)
            serializer = PedidoSerializerOnPut(data = data)
            if serializer.is_valid():
                idPedido = serializer.validated_data['id']
                fechaEntrega = serializer.validated_data['fechaEntrega']
                fechaRecoleccion = serializer.validated_data['fechaRecoleccion']
                pedido = get_object_or_404(Pedido, id=idPedido)
                resultado = self.evaluarNuevasFechas(pedido, fechaEntrega, fechaRecoleccion)
                if(resultado):
                    response = {
                        "errores": resultado,
                    }
                    return Response(response, status=400)
                pedido.fechaEntrega = fechaEntrega
                pedido.fechaRecoleccion = fechaRecoleccion
                pedido.notas = serializer.validated_data['notas']
                pedido.estado = serializer.validated_data['estado']
                pedido.pagoRecibido = serializer.validated_data['pagoRecibido']
                pedido.save()
                return Response(OPERACION_EXITOSA, status=200)
            return JsonResponse(serializer.errors, status=400)
        return Response(NO_MYPE_RESPONSE, status=403)
    
    def delete(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            data = JSONParser().parse(request)
            serializer = PedidoSerializerOnPut(data = data, partial = True)
            if serializer.is_valid():
                idPedido = serializer.validated_data['id']
                pedido = get_object_or_404(Pedido, id = idPedido)
                mobiliario = pedido.mobiliariorentado_set.all()
                cargosExtra = pedido.cargoextra_set.all()
                for m in mobiliario:
                    m.delete()
                for c in cargosExtra:
                    c.delete()
                pedido.delete()
                return Response(OPERACION_EXITOSA, status = 200)
            return JsonResponse(serializer.errors, status=400)
        return Response(NO_MYPE_RESPONSE, status=403)
    
    def get(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if 'Pedido-Id' in request.headers:
            pedido_id = request.headers['Pedido-Id']
            pedido = get_object_or_404(Pedido, id = pedido_id)
            mobRentado = pedido.mobiliariorentado_set.all()
            cargosExtra = pedido.cargoextra_set.all()
            if user.is_mype:
                pedidoSerializer = PedidoGetSerializer(pedido)
                mobiliarioSerializer = GetMobiliarioRentadoSerializer(mobRentado, many = True)
            else:
                pedidoSerializer = PedidoParaClienteSerializer(pedido)
                mobiliarioSerializer = MobiliarioRentadoClienteSerializer(mobRentado, many=True)
            print(mobiliarioSerializer.data)
            cargosSerializer = CargoExtraSerializer(cargosExtra, many=True)
            response = {
                "pedido" : JSONRenderer().render(pedidoSerializer.data),
                "mobiliario" : JSONRenderer().render(mobiliarioSerializer.data),
                "cargos" : JSONRenderer().render(cargosSerializer.data)
            }
            return Response(response, status=200)
        if user.is_mype:
            mype = user.mype
            precio_mobiliario_sum =mype.pedido_set.annotate(total_mobiliario = Sum(F('mobiliariorentado__precio')*F('mobiliariorentado__cantidad'))).filter(pk=OuterRef('pk'))
            cargos_sum = mype.pedido_set.select_related('cliente').annotate(total_cargos = Sum('cargoextra__precio')).filter(pk=OuterRef('pk'))
            pedidos = mype.pedido_set.annotate(
                total_mobiliario = Subquery(precio_mobiliario_sum.values('total_mobiliario'), output_field=FloatField()),
                total_cargos = Subquery(cargos_sum.values('total_cargos'), output_field=FloatField())
            ).order_by(
                Case(
                    When(estado = 'Por entregar', then=1),
                    When(estado = 'Entregado', then=2),
                    When(estado = 'Por recoger', then=3),
                    When(estado = 'Finalizado', then=4),
                    default=5,
                ),
                'fechaEntrega',
            )
            
            serializer = PedidoParaListaSerializer(pedidos, many=True)
            jsonData = JSONRenderer().render(serializer.data)
            return Response(jsonData, status=200)
        return Response(NO_MYPE_RESPONSE, status=400)
    
class PedidosEntregaView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            if 'Pedido-Periodo' in request.headers:
                header = request.headers['Pedido-Periodo']
                fechaIni = ''
                fechaFin = ''
                Tz = pytz.timezone("America/Mexico_City")
                hoy = datetime.now(Tz).date()
                if 'hoy' in header:
                    fechaIni = str(hoy) + ' 00:00Z'
                    fechaFin = str(hoy) + ' 23:59Z'
                else:
                    periodo = timedelta(weeks=1)
                    dateFin = hoy + periodo
                    fechaIni = str(hoy) + ' 00:00Z'
                    fechaFin = str(dateFin) + ' 23:59Z'
                mype = user.mype
                precio_mobiliario_sum =mype.pedido_set.annotate(total_mobiliario = Sum(F('mobiliariorentado__precio')*F('mobiliariorentado__cantidad'))).filter(pk=OuterRef('pk'))
                cargos_sum = mype.pedido_set.select_related('cliente').annotate(total_cargos = Sum('cargoextra__precio')).filter(pk=OuterRef('pk'))
                pedidosQS1 = None
                if 'entregar' in header:
                    pedidosQS1 = mype.pedido_set.filter(fechaEntrega__lte = fechaFin).filter(estado="Por entregar").order_by('fechaEntrega')
                else:
                    pedidosQS1 =mype.pedido_set.filter(fechaRecoleccion__lte = fechaFin).filter(estado="Entregado").order_by('fechaRecoleccion')
                pedidos = pedidosQS1.select_related('cliente').annotate(
                    total_mobiliario = Subquery(precio_mobiliario_sum.values('total_mobiliario'), output_field=FloatField()),
                    total_cargos = Subquery(cargos_sum.values('total_cargos'), output_field=FloatField())
                )
                serializer = PedidoParaListaSerializer(pedidos, many=True)
                jsonData = JSONRenderer().render(serializer.data)
                return Response(jsonData, status=200)
            response = {
                "error": "No se encontro el header esperado Pedido-Periodo",
            }
            return Response(response, status=400)
        return Response(NO_MYPE_RESPONSE, status=400)
    
class GenerarPDFView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            if 'Pedido-Id' in request.headers:
                mype = user.mype
                pedido_id = request.headers['Pedido-Id']
                pedido = get_object_or_404(Pedido, id = pedido_id)
                cliente = get_object_or_404(Cliente, id = pedido.cliente_id)
                direccionCli = cliente.direcciones.all()
                direccionMype = mype.direcciones.all()
                mobRentado = pedido.mobiliariorentado_set.all().annotate(subtotal = F('cantidad') * F('precio'))
                agTotal = mobRentado.aggregate(total_mobiliario=Sum(F('cantidad')*F('precio')))
                cargosExtra = pedido.cargoextra_set.all()
                agCargos = cargosExtra.aggregate(total_cargos=Sum(F('precio')))
                numTotalMob = 0
                numTotalCargos = 0
                numPagado = 0
                if not agTotal['total_mobiliario'] is None:
                   numTotalMob =  agTotal['total_mobiliario']
                if not agCargos['total_cargos'] is None:
                    numTotalCargos = agCargos['total_cargos']
                if not pedido.pagoRecibido is None:
                    numPagado = pedido.pagoRecibido
                context = {
                    'pedido': pedido,
                    'cliente': cliente,
                    'mobRentado': mobRentado,
                    'cargosExtra': cargosExtra,
                    'total': numTotalMob + numTotalCargos,
                    'mype': mype,
                    'direccionCli': direccionCli,
                    'direccionMype': direccionMype,
                    'adeudo': numTotalCargos + numTotalMob - numPagado,
                }
                html = render_to_string("pedido.html", context)
                if os.path.isfile(settings.MEDIA_ROOT + 'pdf/pedido'+user.username+'.pdf'):
                    os.remove(settings.MEDIA_ROOT + 'pdf/pedido'+user.username+'.pdf')
                pdf = generate_pdf(html)
                with open(settings.MEDIA_ROOT + '/pdf/pedido'+user.username+'.pdf', 'wb') as w:
                    w.write(pdf)
                
                response = {
                    "url": settings.MEDIA_URL + 'pdf/pedido' + user.username + '.pdf',
                }
                return Response(response, status=200)
            response = {
                "error": "No se encontro el header esperado Pedido-Id",
            }
        return Response(NO_MYPE_RESPONSE, status=400)
    
@api_view(('GET',))
@authentication_classes([])
@permission_classes([])
@renderer_classes((JSONRenderer,))
def getPedidoPDF(request, id, userId):
    idForm = IdMypeForm({"id":id})
    if idForm.is_valid():
        user = get_object_or_404(Usuario, pk= userId)
        mype = user.mype
        pedido = get_object_or_404(Pedido, id = id)
        cliente = get_object_or_404(Cliente, id = pedido.cliente_id)
        direccionCli = cliente.direcciones.all()
        direccionMype = mype.direcciones.all()
        mobRentado = pedido.mobiliariorentado_set.all().annotate(subtotal = F('cantidad') * F('precio'))
        agTotal = mobRentado.aggregate(total_mobiliario=Sum(F('cantidad')*F('precio')))
        cargosExtra = pedido.cargoextra_set.all()
        agCargos = cargosExtra.aggregate(total_cargos=Sum(F('precio')))
        numTotalMob = 0
        numTotalCargos = 0
        numPagado = 0
        if not agTotal['total_mobiliario'] is None:
            numTotalMob =  agTotal['total_mobiliario']
        if not agCargos['total_cargos'] is None:
            numTotalCargos = agCargos['total_cargos']
        if not pedido.pagoRecibido is None:
            numPagado = pedido.pagoRecibido
        context = {
            'pedido': pedido,
            'cliente': cliente,
            'mobRentado': mobRentado,
            'cargosExtra': cargosExtra,
            'total': numTotalMob + numTotalCargos,
            'mype': mype,
            'direccionCli': direccionCli,
            'direccionMype': direccionMype,
            'adeudo': numTotalCargos + numTotalMob - numPagado,
        }
        html = render_to_string("pedido.html", context)
        pdf = generate_pdf(html)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="pedido_{}_{}.pdf"'.format(mype.nombreEmpresa, pedido.id)
        return response
    errorResponse = '<!doctype html><html><head><title>Error</title></head><body>'+idForm.errors+'</body></html>'
    return HttpResponse(errorResponse, status=400)





