# Generated by Django 4.1.3 on 2023-05-29 05:44

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0019_remove_clienteportelefono_descuento_mype_imagen'),
        ('GestionInventario', '0008_mobiliariorentado_pedido'),
        ('busquedaCotizacion', '0003_comentario_fecha'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolicitudCotizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaEntrega', models.DateTimeField()),
                ('fechaRecoleccion', models.DateTimeField()),
                ('estado', models.CharField(default='Por cotizar', max_length=15)),
                ('clienteWeb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solicitudes_hechas', to='usuarios.clienteweb')),
                ('mype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solicitudes_recibidas', to='usuarios.mype')),
            ],
        ),
        migrations.CreateModel(
            name='MobiliarioPorCotizar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('precio', models.FloatField(blank=True, null=True)),
                ('mobiliario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='por_cotizar', to='GestionInventario.mobiliario')),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articulos', to='busquedaCotizacion.solicitudcotizacion')),
            ],
        ),
        migrations.CreateModel(
            name='CargoExtraCotizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('concepto', models.CharField(max_length=60)),
                ('precio', models.FloatField()),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='busquedaCotizacion.solicitudcotizacion')),
            ],
        ),
    ]