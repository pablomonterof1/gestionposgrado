# Generated by Django 5.2 on 2025-06-17 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0015_matriculausuario_matriculadocentemodulo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilusuario',
            name='rol',
            field=models.IntegerField(blank=True, choices=[(1, 'Estudiante'), (2, 'Docente'), (3, 'Coordinador'), (4, 'Editor'), (5, 'Tutor')], null=True),
        ),
    ]
