# Generated by Django 4.1.3 on 2023-04-16 22:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('GestionInventario', '0007_mobiliariorentado'),
        ('gestionPedidos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobiliariorentado',
            name='pedido',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestionPedidos.pedido'),
        ),
    ]
