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
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



for route in react_routes:
    urlpatterns += [
        re_path(route, views.index, name='homeReact')
    ]
