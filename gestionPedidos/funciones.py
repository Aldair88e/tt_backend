from GestionInventario.models import Mobiliario
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .models import Pedido

def mobiliarioDisponibleEnPeriodo(id_tipo_mobiliario, fechaInicio, fechaFin):
    #Obtener el mobiliario
    mobiliario = get_object_or_404(Mobiliario, id = id_tipo_mobiliario)
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