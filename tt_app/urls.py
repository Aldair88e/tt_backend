"""tt_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from usuarios.views import user_haveData, clienteRegistro, MypeRegistro
from dj_rest_auth.views import PasswordResetConfirmView
from django_postalcodes_mexico import urls as django_postalcodes_mexico_urls
from django.conf import settings
from django.conf.urls.static import static
from indexServerApp import views
from GestionInventario.views import MobiliarioRegistro, MobiliarioMantenimientoView, MobiliarioShortview, MobiliarioPerdidoView, MobiliarioRentadoView
from gestionClientes.views import ClientePorTelefonoView, ListaClientesView, ClientesShortView
from gestionPedidos.views import PedidoView, CargoExtraView, PedidosEntregaView, GenerarPDFView
# from GestionInventario import views as InventarioViews

react_routes = getattr(settings, 'REACT_ROUTES', [])
urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('allauth.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration', include('dj_rest_auth.registration.urls')),
    path('user/', user_haveData.as_view(), name='user'),
    path('cliente/registro', clienteRegistro.as_view(), name='clienteRegistro'),
    path('mype/registro', MypeRegistro.as_view(), name='MypeRegistro'),
    path('dj-rest-auth/password/reset/confirm/<str:uidb64>/<str:token>', PasswordResetConfirmView.as_view(),
            name='password_reset_confirm'),
    path('CP/', include(django_postalcodes_mexico_urls)),
    path('', views.index, name='home'),
    path('mobiliario/', MobiliarioRegistro.as_view(), name='mobiliarioRegistro'),
    path('api/mantenimiento/', MobiliarioMantenimientoView.as_view(), name='mantenimiento'),
    path('api/mobiliario/short/', MobiliarioShortview.as_view(), name='mobiliario_short'),
    path('api/mobiliario/perdido/', MobiliarioPerdidoView.as_view(), name='mobiliario_perdido'),
    path('api/mobiliario/rentado/', MobiliarioRentadoView.as_view(), name='mobiliario_rentado'),
    path('api/gestion-clientes/', ClientePorTelefonoView.as_view(), name='gestion_clientes'),
    path('api/gestion-clientes/lista/', ListaClientesView.as_view(), name='lista_clientes'),
    path('api/gestion-clientes/clientes-short/', ClientesShortView.as_view(), name='Cliente_short'),
    path('api/gestion-pedidos/', PedidoView.as_view(), name='gestion-pedidos'),
    path('api/gestion-pedidos/cargos/', CargoExtraView.as_view(), name='cargos_extra'),
    path('api/gestion-pedidos/entrega/', PedidosEntregaView.as_view(), name='pedidos_por_entregar'),
    path('api/gestion-pedidos/pdf/', GenerarPDFView.as_view(), name='generar_pdf_pedido'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)



for route in react_routes:
    urlpatterns += [
        re_path(route, views.index, name='homeReact')
    ]
