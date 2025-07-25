# Generated by Django 5.2 on 2025-06-23 16:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('programasposgrado', '0013_especialidadesmedicas_programaposgradoem_modulosem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TernaModuloPM',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('docente1_idoneo', models.ManyToManyField(blank=True, related_name='terna_modulopm_idoneo', to=settings.AUTH_USER_MODEL)),
                ('docente2', models.ManyToManyField(blank=True, related_name='terna_modulopm_docente2', to=settings.AUTH_USER_MODEL)),
                ('docente3', models.ManyToManyField(blank=True, related_name='terna_modulopm_docente3', to=settings.AUTH_USER_MODEL)),
                ('modulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terna_modulopm', to='programasposgrado.modulos')),
                ('programa_posgrado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terna_modulopm', to='programasposgrado.programaposgrado')),
            ],
            options={
                'verbose_name': 'Terna de Modulo Maestria',
                'verbose_name_plural': 'Ternas de Modulo Maestria',
            },
        ),
        migrations.CreateModel(
            name='DocenteContratadoPM',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docente_contratadopm', to=settings.AUTH_USER_MODEL)),
                ('terna_modulo_maestria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docente_contratadopm', to='seleccionperfiles.ternamodulopm')),
            ],
            options={
                'verbose_name': 'Docente Contratado',
                'verbose_name_plural': 'Docentes Contratados',
            },
        ),
    ]
