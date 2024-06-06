# Generated by Django 2.2.10 on 2023-01-30 15:35

from django.db import migrations, models
import django.db.models.deletion
import coasmedas.functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuario', '0001_initial'),
        ('contrato', '0001_initial'),
        ('estado', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CcActividad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.IntegerField()),
                ('descripcion', models.TextField()),
                ('inicioprogramado', models.NullBooleanField()),
                ('finprogramado', models.NullBooleanField()),
                ('requiereSoporte', models.NullBooleanField()),
                ('soporteObservaciones', models.NullBooleanField()),
            ],
            options={
                'db_table': 'cronogramacontrato_actividad',
            },
        ),
        migrations.CreateModel(
            name='CcActividadContrato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicioprogramado', models.DateField(blank=True, null=True)),
                ('finprogramado', models.DateField(blank=True, null=True)),
                ('inicioejecutado', models.DateField(blank=True, null=True)),
                ('finejecutado', models.DateField(blank=True, null=True)),
                ('observaciones', models.CharField(blank=True, max_length=150, null=True)),
                ('actividad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='actividadContrato_actividad', to='cronogramacontrato.CcActividad')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='actividadContrato_contrato', to='contrato.Contrato')),
                ('estadofin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='actividadContrato_estadofin', to='estado.Estado')),
                ('estadoinicio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='actividadContrato_estadoinicio', to='estado.Estado')),
            ],
            options={
                'db_table': 'cronogramacontrato_actividadContrato',
                'permissions': (('can_see_cronogramacontrato', 'can see cronogramacontrato'),),
            },
        ),
        migrations.CreateModel(
            name='CcCronograma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'cronogramacontrato_cronograma',
                'ordering': ['nombre', 'activo'],
            },
        ),
        migrations.CreateModel(
            name='CcCapitulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
                ('orden', models.IntegerField()),
                ('cronograma', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cronograma_capitulo', to='cronogramacontrato.CcCronograma')),
            ],
            options={
                'db_table': 'cronogramacontrato_capitulo',
            },
        ),
        migrations.CreateModel(
            name='CcActividadContratoSoporte',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=30)),
                ('archivo', models.FileField(null=True, upload_to=coasmedas.functions.RandomFileName('cronograma_contrato', 'crono_acs'))),
                ('actividadcontrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ActividadContratoSoporte_actividadcontrato', to='cronogramacontrato.CcActividadContrato')),
            ],
            options={
                'db_table': 'cronogramacontrato_actividadContratoSoporte',
            },
        ),
        migrations.CreateModel(
            name='CcActividadContratoResponsable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actividadcontrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ActividadContratoResponsable_actividadcontrato', to='cronogramacontrato.CcActividadContrato')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ActividadContratoResponsable_actividadcontrato', to='usuario.Usuario')),
            ],
            options={
                'db_table': 'cronogramacontrato_actividadContratoResponsable',
            },
        ),
        migrations.AddField(
            model_name='ccactividad',
            name='capitulo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='capitulo_actividad', to='cronogramacontrato.CcCapitulo'),
        ),
    ]
