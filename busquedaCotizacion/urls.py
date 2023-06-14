from django.urls import path

from . import views


app_name = 'busquedaCotizacion'
urlpatterns = [
    # There are postal codes with leading zeros,
    # hence slug is prefered over int
    path(
        'search-by-cp/<slug:postal_code>/',
        views.searchCPString,
        name='search-postal-code-municipio'),
    path(
        'search-by-mnpio/<str:municipio>/',
        views.searchMunicipio,
        name='search-municipios',
    ),
    path(
        'mypes-by-mnpio/<str:municipio>/<slug:estado>/',
        views.searchMypes,
        name='search-mypes-by-mnpio',
    ),
    path(
        'mypes-by-edo/<str:municipio>/<slug:estado>/',
        views.searchMypesEnEstado,
        name='search-mypes-by-edo',
    ),
    path(
        'mype-info/<int:id>/',
        views.getMypeInfo,
        name='get-mype-info',
    ),
    path(
        'registro-solicitud/',
        views.SolicitudCotizacionView.as_view(),
        name='registro-solicitud-cotizacion',
    ),
    path(
        'get-solicitud/<int:id>/',
        views.getSolicitudCotizacion,
        name='get-solicitud-cotizacion',
    ),
    path(
        'put-mobiliario-cotizar/',
        views.putMobiliarioPorCotizar,
        name='put-mobiliario-por-cotizar',
    ),
    path(
        'cargos-extra/',
        views.CargoExtraCotizacionView.as_view(),
        name = 'cargos-extra-cotizacion',
    ),
    path(
        'get-pedidos-externos/',
        views.getSolicitudesDeNuevoPedido,
        name = 'get-pedidos-externos',
    ),
    path(
        'get-pedidos-cliente/',
        views.getPedidosCliente,
        name = 'get-pedidos-cliente',
    ),
    path(
        'comentario/',
        views.ComentariosView.as_view(),
        name = 'comentarios',
    ),
    path(
        'disponibilidad/',
        views.getDisponibilidadMobiliario,
        name = 'disponibilidad',
    )
]