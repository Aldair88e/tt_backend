# Generated by Django 4.1.3 on 2023-03-28 22:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0017_alter_clienteportelefono_descuento'),
        ('GestionInventario', '0004_mobiliarioenmantenimiento'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobiliarioPerdido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('totalReposicion', models.FloatField(blank=True)),
                ('pagoRecibido', models.FloatField(blank=True)),
                ('fecha', models.DateField(auto_now_add=True)),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.cliente')),
                ('mobiliario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='GestionInventario.mobiliario')),
            ],
        ),
    ]