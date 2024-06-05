# Generated by Django 2.2.10 on 2023-01-30 15:31

from django.db import migrations, models
import django.db.models.deletion
import sinin4.functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('proyecto', '0001_initial'),
        ('tipo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ALote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=300, null=True)),
                ('direccion', models.CharField(blank=True, max_length=300, null=True)),
                ('cantidad_estructura', models.IntegerField(blank=True, default=0, null=True)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='p_p_construccion_lote_proyecto', to='proyecto.Proyecto')),
            ],
            options={
                'verbose_name': 'Lote',
                'db_table': 'p_p_construccion_lote',
                'permissions': (('can_see_ALote', 'can_see_ALote'),),
            },
        ),
        migrations.CreateModel(
            name='DPropietario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cedula', models.CharField(blank=True, max_length=300, null=True, unique=True)),
                ('nombres', models.CharField(blank=True, max_length=300, null=True)),
                ('apellidos', models.CharField(blank=True, max_length=300, null=True)),
                ('telefono', models.CharField(blank=True, max_length=200, null=True)),
                ('correo', models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={
                'verbose_name': 'Propietario',
                'db_table': 'p_p_construccion_propietario',
                'permissions': (('can_see_DPropietario', 'can_see_DPropietario'),),
            },
        ),
        migrations.CreateModel(
            name='EPropietarioLote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lote', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='p_p_construccion_propietario_lote_lote', to='p_p_construccion.ALote')),
                ('propietario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='p_p_construccion_propietario_lote_propietario', to='p_p_construccion.DPropietario')),
            ],
            options={
                'verbose_name': 'Propietario lote',
                'db_table': 'p_p_construccion_propietario_lote',
                'permissions': (('can_see_EPropietarioLote', 'can_see_EPropietarioLote'),),
            },
        ),
        migrations.CreateModel(
            name='CEstructura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(blank=True, max_length=100, null=True)),
                ('lote', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='p_p_construccion_estructura_lote', to='p_p_construccion.ALote')),
            ],
            options={
                'verbose_name': 'Estructura',
                'db_table': 'p_p_construccion_estructura',
                'permissions': (('can_see_CEstructura', 'can_see_CEstructura'),),
            },
        ),
        migrations.CreateModel(
            name='BSoporte',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('soporte', models.FileField(blank=True, null=True, upload_to=sinin4.functions.RandomFileName('lote/soporte'))),
                ('nombre', models.CharField(blank=True, max_length=300, null=True)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='p_p_construccion_soporte_proyecto', to='proyecto.Proyecto')),
                ('tipo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='p_p_construccion_soporte_tipo', to='tipo.Tipo')),
            ],
            options={
                'verbose_name': 'Soporte',
                'db_table': 'p_p_construccion_soporte',
                'permissions': (('can_see_BSoporte', 'can_see_BSoporte'),),
            },
        ),
    ]