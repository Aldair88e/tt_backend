# Generated by Django 4.1.3 on 2023-03-31 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GestionInventario', '0005_mobiliarioperdido'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobiliarioenmantenimiento',
            name='fechaFin',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mobiliarioperdido',
            name='pagoRecibido',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='mobiliarioperdido',
            name='totalReposicion',
            field=models.FloatField(blank=True, null=True),
        ),
    ]