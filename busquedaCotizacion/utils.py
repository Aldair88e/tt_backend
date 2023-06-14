from django_postalcodes_mexico.models import PostalCode 
from usuarios.models import Mype, Direccion
from django.shortcuts import get_object_or_404
from django.db.models import Sum
MAX_RESULTS = 8

def searchByMunicipio(city):
    postal_codes = PostalCode.objects.filter(D_mnpio__istartswith=city).order_by("D_mnpio").distinct("D_mnpio")
    if postal_codes:
        municipios_list = []
        if len(postal_codes) > MAX_RESULTS:
            for i in range(MAX_RESULTS):
                municipios_list.append({
                    "municipio": postal_codes[i].D_mnpio,
                    "estado": postal_codes[i].c_estado,
                })
            return {"municipios": municipios_list}
        for postal_code in postal_codes:
            municipios_list.append({
                "municipio": postal_code.D_mnpio,
                "estado": postal_code.c_estado,
            })
        return {"municipios": municipios_list}
    return dict()

def searchByCP(postal_code):
    postal_codes = PostalCode.objects.filter(d_codigo__startswith=postal_code).distinct(
        "d_codigo"
    )
    if postal_codes:
        if len(postal_codes) > MAX_RESULTS:
            codigos_list = []
            for i in range(MAX_RESULTS):
                codigos_list.append(str(postal_codes[i]))
            return {"municipios": codigos_list}
        codigos_list = [str(cp) for cp in postal_codes]
        return {"municipios": codigos_list}
    return dict()

def searchMypesByMunicipio(municipio):
    postal_codes = PostalCode.objects.filter(D_mnpio = municipio).values_list('d_codigo', flat=True)
    direcciones = Direccion.objects.filter(codigoPostal__in = postal_codes).values_list('mype__usuario_id', flat=True)
    print(direcciones)
    mypes = Mype.objects.filter(usuario_id__in=direcciones)
    print(mypes)
    return mypes

def searchMypesByEstado(estado):
    postal_codes = PostalCode.objects.filter(c_estado = estado).values_list('d_codigo', flat = True)
    print(postal_codes)
    direcciones = Direccion.objects.filter(codigoPostal__in = postal_codes).values_list('mype__usuario_id', flat=True)
    print(direcciones)
    mypes = Mype.objects.filter(usuario_id__in = direcciones)
    print(mypes)
    return mypes


def mobiliarioDisponibleEnPeriodo(mobiliario, fechaInicio, fechaFin):
    #Obtener el mobiliario rentado cuya fecha de entrega esté entre la fecha de inicio y la fecha de fin
    mobiliarioRentado1 = mobiliario.mobiliariorentado_set.select_related("pedido").filter(pedido__fechaEntrega__gte=fechaInicio).filter(pedido__fechaEntrega__lte=fechaFin)
    # pedidos1 = Pedido.objects.all().filter(fechaEntrega__gte=fechaInicio).filter(fechaEntrega__lte=fechaFin)
    # Obtener el mobiliario rentado cuya fecha de recoleccion este entre la fecha de inicio y de fin
    mobiliarioRentado2 = mobiliario.mobiliariorentado_set.select_related("pedido").filter(pedido__fechaRecoleccion__gte=fechaInicio).filter(pedido__fechaRecoleccion__lte=fechaFin)
    # Combinar las dos tablas y sumar la columna cantidad
    mobiliarioDuplicado = mobiliarioRentado2.filter(id__in=mobiliarioRentado1)
    resultadoAgregate = mobiliarioRentado1.aggregate(cantidad_1=Sum('cantidad'))
    cantidad1 = 0
    cantidad2 = 0
    cantidad3 = 0
    if not resultadoAgregate['cantidad_1'] is None:
        cantidad1 = resultadoAgregate['cantidad_1']
    resultadoAgregate = mobiliarioRentado2.aggregate(cantidad_2=Sum('cantidad'))
    if not resultadoAgregate['cantidad_2'] is None:
        cantidad2 = resultadoAgregate['cantidad_2']
    resultadoAgregate = mobiliarioDuplicado.aggregate(cantidad_3=Sum('cantidad'))
    if not resultadoAgregate['cantidad_3'] is None:
        cantidad3 = resultadoAgregate['cantidad_3']
    cantidadRentado = cantidad1 + cantidad2 - cantidad3
    print(cantidadRentado)
    #Obtener el mobiliario en mantenimiento
    mobiliarioMantenimiento2 = mobiliario.mobiliarioenmantenimiento_set.filter(fechaFin__gte=fechaInicio).filter(fechaFin__lte=fechaFin)
    mobiliarioMantenimiento3 = mobiliario.mobiliarioenmantenimiento_set.filter(fechaFin__isnull=True)
    resultadoAggregate = mobiliarioMantenimiento2.aggregate(cantidad_sum=Sum('cantidad'))
    cantidadMant1 = 0
    cantidadMant2 = 0
    if not resultadoAggregate['cantidad_sum'] is None:  
        cantidadMant1 = resultadoAggregate['cantidad_sum']    
    resultadoAggregate = mobiliarioMantenimiento3.aggregate(cantidad_sum=Sum('cantidad'))
    if not resultadoAggregate['cantidad_sum'] is None: 
        cantidadMant2 = resultadoAggregate['cantidad_sum']
    cantidadMantenimiento = cantidadMant1 + cantidadMant2

    #Obtener el mobiliario perdido
    mobPerdido = mobiliario.mobiliarioperdido_set.all()
    cantidadPerdido = 0
    if mobPerdido.exists():
        resultado = mobPerdido.aggregate(Sum('cantidad'))
        cantidadPerdido = resultado['cantidad__sum']
    return mobiliario.total - cantidadRentado - cantidadPerdido - cantidadMantenimiento;