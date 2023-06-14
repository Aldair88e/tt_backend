from django.shortcuts import render, get_object_or_404
from rest_framework import views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, OuterRef, Count, Subquery, FloatField, IntegerField, Case, When
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from usuarios.models import Mype, Usuario
from GestionInventario.models import Mobiliario
from .serializers import MypeListaSerializer, MypeSerializer, MobiliarioSerializer, ComentarioSerializer, SolicitudCotizacionSerializer, MobiliarioPorCotizarSerializer, IdSerializer, SolicitudMypeViewSerializer, SolicitudClienteViewSerializer, MobiliarioPorCotizarGetSerializer, CargoCotizacionPostSerializer, CargoCotizacionSerializer, MobiliarioPorCotizarPutListSerializer, MobiliarioPorPedirSerializer, PedidoClienteSerializer, ComentarioFullSerializer, MobiliarioDisponibleSerializer
from .utils import searchByCP, searchByMunicipio, searchMypesByMunicipio, searchMypesByEstado
from .forms import MunicipioForm, CodigoEstadoForm, IdMypeForm
from .models import SolicitudCotizacion, MobiliarioPorCotizar, CargoExtraCotizacion
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes, parser_classes
try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _

from django_postalcodes_mexico.forms import PostalCodeSearchForm
from GestionInventario.constantes import OPERACION_EXITOSA, NO_MYPE_RESPONSE
from .utils import mobiliarioDisponibleEnPeriodo


# Create your views here.
def searchCPString(request, postal_code):
    postalCodeForm = PostalCodeSearchForm({"postal_code": postal_code})
    if postalCodeForm.is_valid():
        postal_codes_list = searchByCP(postal_code)
        status = 200 if postal_codes_list else 404
        return JsonResponse(postal_codes_list, status=status)
    return JsonResponse(postalCodeForm.errors, status=400)

def searchMunicipio(request, municipio):
    municipioForm = MunicipioForm({"municipio": municipio})
    if municipioForm.is_valid():
        municipios_list = searchByMunicipio(municipio)
        status = 200 if municipios_list else 404
        return JsonResponse(municipios_list, status=status)
    return JsonResponse(municipioForm.errors, status=400)

@api_view(('GET',))
@authentication_classes([])
@permission_classes([])
@renderer_classes((JSONRenderer,))
def searchMypes(request, municipio, estado):
    municipioForm = MunicipioForm({"municipio":municipio})
    if municipioForm.is_valid():
        mypes_qs = searchMypesByMunicipio(municipio)
        calificaciones_avg = Mype.objects.annotate(promedio_calificaciones = Avg('comentarios__calificacion')).filter(pk=OuterRef('pk'))
        comentarios_count = Mype.objects.annotate(total_comentarios = Count('comentarios__comentario_texto')).filter(pk=OuterRef('pk'))
        mypes_qs = mypes_qs.annotate(
            promedio_calificaciones = Subquery(calificaciones_avg.values('promedio_calificaciones'), output_field=FloatField()),
            total_comentarios = Subquery(comentarios_count.values('total_comentarios'), output_field=IntegerField())
        )
        serializer = MypeListaSerializer(mypes_qs, many=True)
        jsonData = JSONRenderer().render(serializer.data)
        return Response(jsonData, status=200)
    print(municipioForm.errors)
    return JsonResponse(municipioForm.errors, status=400)

@api_view(('GET',))
@authentication_classes([])
@permission_classes([])
@renderer_classes((JSONRenderer,))
def searchMypesEnEstado(request, municipio, estado):
    estadoForm = CodigoEstadoForm({"estado":estado})
    if estadoForm.is_valid():
        mypes_qs = searchMypesByEstado(estado)
        calificaciones_avg = Mype.objects.annotate(promedio_calificaciones = Avg('comentarios__calificacion')).filter(pk=OuterRef('pk'))
        comentarios_count = Mype.objects.annotate(total_comentarios = Count('comentarios__comentario_texto')).filter(pk=OuterRef('pk'))
        mypes_qs = mypes_qs.annotate(
            promedio_calificaciones = Subquery(calificaciones_avg.values('promedio_calificaciones'), output_field=FloatField()),
            total_comentarios = Subquery(comentarios_count.values('total_comentarios'), output_field=IntegerField())
        )
        serializer = MypeListaSerializer(mypes_qs, many=True)
        jsonData = JSONRenderer().render(serializer.data)
        return Response(jsonData, status=200)
    print(estadoForm.errors)
    return JsonResponse(estadoForm.errors, status=400)

@api_view(('GET',))
@authentication_classes([])
@permission_classes([])
@renderer_classes((JSONRenderer,))
def getMypeInfo(request, id):
    idForm = IdMypeForm({"id":id})
    if idForm.is_valid():
        mype = get_object_or_404(Mype, pk = id)
        mobiliarioList = mype.mobiliario_set.all()
        comentariosList = mype.comentarios.all()
        comentariosExtraInfo = comentariosList.aggregate(promedio = Avg('calificacion'), total_comentarios=Count('*'))
        mypeSerializer = MypeSerializer(mype)
        mobiliarioSerializer = MobiliarioSerializer(mobiliarioList, many=True)
        comentarioSerializer = ComentarioSerializer(comentariosList, many=True)
        response = {
            "mype": JSONRenderer().render(mypeSerializer.data),
            "mobiliario" : JSONRenderer().render(mobiliarioSerializer.data),
            "comentarios" : JSONRenderer().render(comentarioSerializer.data),
            "total_comentarios": comentariosExtraInfo['total_comentarios'],
            "calificacion": comentariosExtraInfo['promedio'],
        }
        return Response(response, status= 200)
    return JsonResponse(idForm.errors, status=400)

class SolicitudCotizacionView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = JSONParser().parse(request)
        serializerSolicitud = SolicitudCotizacionSerializer(data=data['solicitudCotizar'])
        if serializerSolicitud.is_valid():
            instanciaSolicitud = serializerSolicitud.save()
            dataMobiliario = data['mobiliario']
            for d in dataMobiliario:
                d['solicitud'] = instanciaSolicitud.id
            serializerMobiliario = MobiliarioPorCotizarSerializer(data=dataMobiliario, many=True)
            if serializerMobiliario.is_valid():
                lista = serializerMobiliario.save()
                return Response({
                    'Solicitud': serializerSolicitud.data,
                })
            instanciaSolicitud.delete()
            return JsonResponse(serializerMobiliario.errors, status=400)
        return JsonResponse(serializerSolicitud.errors, status=400)
    
    def delete(self, request):
        data = JSONParser().parse(request)
        serializerId= IdSerializer(data=data)
        if serializerId.is_valid():
            idSolicitud = serializerId.validated_data['id']
            solicitud = get_object_or_404(SolicitudCotizacion, pk=idSolicitud)
            listaCargos = solicitud.cargos.all()
            listaMobiliario = solicitud.articulos.all()
            for l in listaMobiliario:
                l.delete()
            for c in listaCargos:
                c.delete()
            solicitud.delete()
            return Response(OPERACION_EXITOSA, status=200)
        return JsonResponse(serializerId.errors,status = 400)
    
    def get(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            mype = user.mype
            listaSolicitudes = mype.solicitudes_recibidas.filter(estado = 'Por cotizar')
            serializer = SolicitudMypeViewSerializer(listaSolicitudes, many=True)
            jsonData = JSONRenderer().render(serializer.data)
            return Response(jsonData, status=200)
        clienteWeb = user.clienteweb
        listaSolicitudes = clienteWeb.solicitudes_hechas.all().order_by( 
                                                                       Case(
                                                                        When(estado='Cotizado', then=1),
                                                                        When(estado='Rechazado', then=2),
                                                                        When(estado='Por cotizar', then=3),
                                                                        default=4,
                                                                       ),
                                                                       'fechaEntrega')
        serializer = SolicitudClienteViewSerializer(listaSolicitudes, many=True)
        jsonData = JSONRenderer().render(serializer.data)
        return Response(jsonData, status=200)
    
    def put(self, request):
        data = JSONParser().parse(request)
        idSolicitud = data['id']
        solicitud = get_object_or_404(SolicitudCotizacion, pk=idSolicitud)
        serializerSolicitud = SolicitudCotizacionSerializer(solicitud, data=data['solicitud'], partial=True)
        if serializerSolicitud.is_valid():
            if 'mobiliario' in data:
                mobiliario = data['mobiliario']
                listaIds = []
                for m in mobiliario:
                    listaIds.append(m['id']);
                print(listaIds)
                mobiliarioList = MobiliarioPorCotizar.objects.filter(id__in = listaIds)
                print(mobiliarioList)
                serializerMobiliario = MobiliarioPorCotizarPutListSerializer(instance=mobiliarioList, data=mobiliario, many=True, partial=True)
                if serializerMobiliario.is_valid():
                    listaNueva = serializerMobiliario.update(serializerMobiliario.instance, serializerMobiliario.validated_data)
                    solicitudNueva = serializerSolicitud.save()
                    return Response(OPERACION_EXITOSA, status = 200)
                print(serializerMobiliario.errors)
                return JsonResponse(serializerMobiliario.errors, status=400)
            solicitudNueva = serializerSolicitud.save()
            return Response(OPERACION_EXITOSA, status=200)
        return JsonResponse(serializerSolicitud.errors, status= 400)
                


@api_view(('GET',))
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes((JSONRenderer,))
def getSolicitudesDeNuevoPedido(request):
    user = get_object_or_404(Usuario, username = request.user)
    if user.is_mype:
        mype = user.mype
        listaSolicitudes = mype.solicitudes_recibidas.filter(estado = 'Pedido enviado').order_by('fechaEntrega')
        serializer = SolicitudMypeViewSerializer(listaSolicitudes, many=True)
        jsonData = JSONRenderer().render(serializer.data)
        return Response(jsonData, status=200)
    return Response(NO_MYPE_RESPONSE, status=403)


@api_view(('GET',))
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes((JSONRenderer,))
def getPedidosCliente(request):
    user = get_object_or_404(Usuario, username = request.user)
    if not user.is_mype:
        cliente = user.clienteweb.cliente
        listaPedidos = cliente.pedido_set.all().order_by(
            Case(
                When(estado='Por entregar', then=1),
                When(estado='Entregado', then=2),
                When(estado='Finalizado', then=3),
                default=4
            ),
            'fechaEntrega'
        )
        serializer = PedidoClienteSerializer(listaPedidos, many=True)
        jsonData = JSONRenderer().render(serializer.data)
        return Response(jsonData, status=200)
    return Response(NO_MYPE_RESPONSE, status=403)
    
@api_view(('GET',))
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes((JSONRenderer,))
def getSolicitudCotizacion(request, id):
    idForm = IdMypeForm({"id":id})
    if idForm.is_valid():
        user = get_object_or_404(Usuario, username= request.user)
        solicitud = get_object_or_404(SolicitudCotizacion, pk = id)
        mobiliarioList = solicitud.articulos.all().select_related('mobiliario').select_related('solicitud')
        cargosExtra = solicitud.cargos.all()
        if user.is_mype:
            solicitudSerializer = SolicitudMypeViewSerializer(solicitud)
        else:
            solicitudSerializer = SolicitudClienteViewSerializer(solicitud)
        if solicitud.estado == 'Pedido enviado':
            mobiliarioSerializer = MobiliarioPorPedirSerializer(mobiliarioList, many = True)
        else:
            mobiliarioSerializer = MobiliarioPorCotizarGetSerializer(mobiliarioList, many=True)
        cargosSerializer = CargoCotizacionSerializer(cargosExtra, many=True)
        response = {
            "solicitud": JSONRenderer().render(solicitudSerializer.data),
            "mobiliario" : JSONRenderer().render(mobiliarioSerializer.data),
            "cargos" : JSONRenderer().render(cargosSerializer.data),
        }
        return Response(response, status= 200)
    return JsonResponse(idForm.errors, status=400)

@api_view(('PUT',))
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes((JSONRenderer,))
@parser_classes((JSONParser,))
def putMobiliarioPorCotizar(request):
    data = JSONParser().parse(request)
    mueble = get_object_or_404(MobiliarioPorCotizar, pk=data['id'])
    serializer = MobiliarioPorCotizarGetSerializer(mueble, data=data['datos'], partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status= 200)
    return JsonResponse(serializer.errors, status=400)


class CargoExtraCotizacionView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = JSONParser().parse(request)
        serializer = CargoCotizacionPostSerializer(data=data)
        if serializer.is_valid():
            instancia = serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    
    def put(self, request):
        data = JSONParser().parse(request)
        instancia = get_object_or_404(CargoExtraCotizacion, pk=data['id'])
        serializer = CargoCotizacionPostSerializer(instancia, data=data['datos'], partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)
    
    def delete(self, request):
        data = JSONParser().parse(request)
        instancia = get_object_or_404(CargoExtraCotizacion, pk=data['id'])
        instancia.delete()
        return Response(OPERACION_EXITOSA, 200)
    
class ComentariosView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(Usuario, username = request.user)
        data = JSONParser().parse(request)
        data['cliente'] = user.clienteweb.cliente.id
        serializer = ComentarioFullSerializer(data=data)
        if serializer.is_valid():
            instancia = serializer.save()
            return Response(OPERACION_EXITOSA, 200)
        return JsonResponse(serializer.errors, status=400)

@api_view(('POST',))
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes((JSONRenderer,))
def getDisponibilidadMobiliario(request):
    data = JSONParser().parse(request)
    serializer = MobiliarioDisponibleSerializer(data=data)
    if serializer.is_valid():
        articulo = get_object_or_404(Mobiliario, pk = serializer.validated_data['id'])
        disponible = mobiliarioDisponibleEnPeriodo(articulo, serializer.validated_data['fechaInicio'], serializer.validated_data['fechaFin'])
        
        response = {
            "id" : articulo.id,
            "disponible": disponible,
        }
        return Response(response, status= 200)
    return JsonResponse(serializer.errors, status=400)

    


 