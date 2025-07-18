# Generated by Django 5.2.3 on 2025-07-02 01:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Medicamento',
            fields=[
                ('id_alfabeta', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre_comercial', models.CharField(max_length=255)),
                ('precio_caja', models.DecimalField(decimal_places=2, max_digits=16)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=16)),
                ('estado', models.IntegerField(choices=[(0, 'Habilitado'), (1, 'Descontinuado')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Laboratorio',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Monodroga',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegistroCarga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fuente', models.CharField(max_length=50, unique=True)),
                ('fecha_carga', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Equivalencia',
            fields=[
                ('medicamento_alfabeta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='core.medicamento')),
            ],
        ),
        migrations.CreateModel(
            name='HistorialPrecio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precio_caja', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('medicamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historial_precios', to='core.medicamento')),
            ],
        ),
        migrations.AddField(
            model_name='medicamento',
            name='laboratorio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.laboratorio'),
        ),
        migrations.AddField(
            model_name='medicamento',
            name='monodroga',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.monodroga'),
        ),
    ]
