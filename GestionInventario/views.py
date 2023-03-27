from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import views
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from usuarios.models import Usuario
from .models import Mobiliario, MobiliarioEnMantenimiento
from .serializers import MobiliarioSerializer, MobiliarioMantenimientoFullSerializer, MantenimientoOnGetSerializer, MantenimientoDelete, MantenimientoPutSerializer, MobiliarioShortSerializer
from django.http import JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.db.models import Sum
from django.http import Http404


# Create your views here.

class MobiliarioShortview(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        mypeObject = user.mype
        mobiliario = mypeObject.mobiliario_set.all()
        serializer = MobiliarioShortSerializer(mobiliario, many=True)
        jsonData = JSONRenderer().render(serializer.data)
        return Response(jsonData, status=200)

class MobiliarioRegistro(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            mypeObject = user.mype
            datos = request.POST
            nombre = datos.get('nombre')
            total = datos.get('total') 
            if nombre is None:
                response = {
                    "nombre": "Este campo es obligatorio",
                }
                return Response(response, status = 400)
            if not nombre:
                response = {
                    "nombre": "Este campo es obligatorio",
                }
                return Response(response, status = 400)
            if len(nombre)>50:
                response = {
                    'nombre': 'La longitud del nombre no es aceptable',
                }
                return Response(response, status=400)
            
            if total is None:
                response = {
                    "nombre": "Este campo es obligatorio",
                }
                return Response(response, status = 400)
            if not total:
                response = {
                    "total": "Este campo es obligatorio",
                }
                return Response(response, status = 400)
            datosNuevos = {}
            datosNuevos['total'] = int(total)
            datosNuevos['nombre'] = nombre
            precioCompra = datos.get('precioCompra')
            precioRenta = datos.get('precioRenta')
            descripcion = datos.get('descripcion')
            proveedor = datos.get('proveedor')
            if precioCompra:
                datosNuevos['precioCompra'] = float(precioCompra) 
            if precioRenta:
                datosNuevos['precioRenta'] = float(precioRenta)
            if descripcion:
                datosNuevos['descripcion'] = descripcion
            if proveedor:
                if len(proveedor) > 50:
                    response = {
                        'proveedor': 'El nombre del proveedor es demasiado grande',
                    }
                    return Response(response, status=400)
                datosNuevos['proveedor'] = proveedor
            imagen = request.FILES.get('imagen') 
            mobiliario = Mobiliario.objects.create(mype = mypeObject, imagen = imagen, **datosNuevos)
            serializer = MobiliarioSerializer(mobiliario)
            return JsonResponse(serializer.data, status=201)
        response = {
            'usuario' : 'El usuario no es de tipo MYPE',
        }
        return  Response(response, status = 400)
    
    def get(self, request):
        usuario = get_object_or_404(Usuario, username= self.request.user)
        if usuario.is_mype:
            mypeObject = usuario.mype
            mobiliario = mypeObject.mobiliario_set.annotate(total_mantenimiento = Sum('mobiliarioenmantenimiento__cantidad'))
            serializer = MobiliarioSerializer(mobiliario, many=True)
            jsonData = JSONRenderer().render(serializer.data)
            return Response(jsonData, status=200)
        response = {
            'usuario' : 'El usuario no es de tipo MYPE',
        }
        return Response(response, status=400)

    def put(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            mypeObject = user.mype
            print(request.POST)
            datos = request.POST
            mobiliarioObject = mypeObject.mobiliario_set.filter(id=datos.get('id'))[0]
            # mobiliarioObject = get_object_or_404(Mobiliario, id = datos.get('id'))
            nombre = datos.get('nombre')
            total = datos.get('total')
            precioCompra = datos.get('precioCompra')
            precioRenta = datos.get('precioRenta')
            descripcion = datos.get('descripcion')
            proveedor = datos.get('proveedor')
            imagen = request.FILES.get('imagen')
            if nombre is not None:
                if len(nombre)<1 and len(nombre)>50:
                    response = {
                        'nombre': 'La longitud del nombre no es aceptable',
                    }
                    return Response(response, status=400)
                mobiliarioObject.nombre = nombre
            if total:
                mobiliarioObject.total = int(total)
            else:
                response = {
                    'Total de Unidades':'Este campo es obligatorio', 
                }
                return Response(response, status=400)
            if precioCompra:
                mobiliarioObject.precioCompra = float(precioCompra)
            else:
                mobiliarioObject.precioCompra = None
            if precioRenta: 
                mobiliarioObject.precioRenta = float(precioRenta)
            else:
                mobiliarioObject.precioRenta = None
            mobiliarioObject.descripcion = descripcion
            if proveedor:
                if len(proveedor) > 50:
                    response = {
                        'proveedor': 'El nombre del proveedor es demasiado grande',
                    }
                    return Response(response, status=400)
            mobiliarioObject.proveedor = proveedor
            if imagen is not None:
                mobiliarioObject.imagen = imagen
            mobiliarioObject.save()
            serializer = MobiliarioSerializer(mobiliarioObject)
            print(serializer.data)
            return JsonResponse(serializer.data, status=200)
        response = {
            'usuario' : 'El usuario no es de tipo MYPE',
        }
        return Response(response, status=400)

    def delete(self, request):
        user = get_object_or_404(Usuario, username = self.request.user)
        if user.is_mype:
            mypeObject = user.mype
            data = JSONParser().parse(request)
            print(data.get('id'))
            instances = mypeObject.mobiliario_set.filter(id=data.get('id'))
            if instances.exists():
                for instance in instances:
                    instance.delete()
                mobiliario = mypeObject.mobiliario_set.all()
                serializer = MobiliarioSerializer(mobiliario, many=True)
                jsonData = JSONRenderer().render(serializer.data)
                return Response(jsonData, status=200)
            response = {
                'error':'El registro no existe en la base de datos'
            } 
            return Response(response, status=400)
        response = {
            'usuario':'El usuario no es de tipo MYPE'
        } 
        return Response(response, status=400)
                
class MobiliarioMantenimientoView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]



    def post(self, request):
        usuario = get_object_or_404(Usuario, username= self.request.user)
        if usuario.is_mype:
            data = JSONParser().parse(request)
            serializer = MobiliarioMantenimientoFullSerializer(data=data)
            print(data)
            if serializer.is_valid():
                mobiliarioDatos = serializer.validated_data['mobiliario']
                mantenimientoDatos = serializer.validated_data['mobiliarioMantenimiento']
                try:
                    mobiliarioInstancia = Mobiliario.objects.annotate(total_mantenimiento=Sum('mobiliarioenmantenimiento__cantidad')).get(id=mobiliarioDatos['id'])
                    if mobiliarioInstancia.total_mantenimiento is None:
                        if (mobiliarioInstancia.total-int(mantenimientoDatos['cantidad'])) < 0:
                            response = {
                                "Overflow":"La cantidad de mobiliario en mantenimiento no puede superar al total del mobiliario",
                            }
                            return Response(response, status=400)
                    else:
                        if (mobiliarioInstancia.total-int(mantenimientoDatos['cantidad']) - mobiliarioInstancia.total_mantenimiento) < 0:
                            response = {
                                "Overflow":"La cantidad de mobiliario en mantenimiento no puede superar al total del mobiliario",
                            }
                            return Response(response, status=400)     
                    mantenimientoInstancia = MobiliarioEnMantenimiento.objects.create(mobiliario=mobiliarioInstancia, **mantenimientoDatos)  
                    response = {
                        "respuesta":"El mobiliario se puso en mantenimiento",
                    }
                    return Response(response, status=201)
                except Mobiliario.DoesNotExist:
                    raise Http404()
            return JsonResponse(serializer.errors, status=400)
        response = {
            'usuario':'El usuario no es de tipo MYPE'
        } 
        return Response(response, status=400)

    def get(self, request):
        usuario = get_object_or_404(Usuario, username= self.request.user)
        if usuario.is_mype:
            mypeInstance = usuario.mype
            qs1 = mypeInstance.mobiliario_set.all()
            qs = MobiliarioEnMantenimiento.objects.select_related('mobiliario').all()
            qr = qs.filter(mobiliario_id__in=qs1)
            serializer = MantenimientoOnGetSerializer(qr, many=True)
            print(serializer.data)
            jsonData = JSONRenderer().render(serializer.data)
            return Response(jsonData, status=200)
        response = {
            'usuario':'El usuario no es de tipo MYPE'
        } 
        return Response(response, status=400)
    
    def delete(self, request):
        usuario = get_object_or_404(Usuario, username= self.request.user)
        if usuario.is_mype:
            data = JSONParser().parse(request)
            serializer = MantenimientoDelete(data=data)
            if serializer.is_valid():
                idM = serializer.validated_data['id']
                mantenimientoInstancia = get_object_or_404(MobiliarioEnMantenimiento, id=idM)
                mantenimientoInstancia.delete()
                response = {
                    "resultado": "Se eliminó correctamente",
                }
                return Response(response, status=200)
            return JsonResponse(serializer.errors, status=400)
        response = {
            'usuario':'El usuario no es de tipo MYPE'
        } 
        return Response(response, status=400)
    def put(self, request):
        usuario = get_object_or_404(Usuario, username= self.request.user)
        if usuario.is_mype:
            data = JSONParser().parse(request)
            serializer = MantenimientoPutSerializer(data=data)
            if serializer.is_valid():
                idM = serializer.validated_data['id']
                mantenimientoInstancia = get_object_or_404(MobiliarioEnMantenimiento, id=idM)
                mantenimientoInstancia.cantidad = serializer.validated_data['cantidad']
                mantenimientoInstancia.fechaFin = serializer.validated_data['fechaFin']
                mantenimientoInstancia.save()
                response = {
                    "resultado": "La operación ser realizó con éxito",
                }
                return Response(response, status=200)
            return JsonResponse(serializer.errors, status=400)
        response = {
            'usuario':'El usuario no es de tipo MYPE'
        } 
        return Response(response, status=400)