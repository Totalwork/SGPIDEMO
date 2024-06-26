# Generated by Django 2.2.10 on 2023-01-20 22:33

from django.db import migrations, models
import django.db.models.deletion
import coasmedas.functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('empresa', '0001_initial'),
        ('parametrizacion', '0001_initial'),
        ('estado', '0001_initial'),
        ('tipo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActaAsignacionRecursos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=4000)),
                ('fechafirma', models.DateField()),
                ('soporte', models.FileField(upload_to=coasmedas.functions.RandomFileName('contrato', 'cto'))),
            ],
            options={
                'db_table': 'contrato_actaasignacionrecursos',
            },
        ),
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250)),
            ],
            options={
                'db_table': 'contrato_actividad',
            },
        ),
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=4000)),
                ('numero', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=4000)),
                ('activo', models.BooleanField(default=True)),
                ('fecha_acta_inicio', models.DateField(blank=True, null=True)),
                ('fecha_firma', models.DateField(blank=True, null=True)),
                ('fechaAdjudicacion', models.DateField(blank=True, null=True)),
                ('contratante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_contratante', to='empresa.Empresa')),
                ('contratista', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_contratista', to='empresa.Empresa')),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='estado.Estado')),
                ('fondo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_contrato_fondo', to='tipo.Tipo')),
                ('mcontrato', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
                ('tipo_contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tipo.Tipo')),
            ],
            options={
                'db_table': 'contrato',
                'ordering': ['nombre'],
                'permissions': (('can_see_contrato', 'can see contrato'), ('can_see_informe_ejcutivo', 'can see informe ejcutivo'), ('can_see_informe_interventoria_dispac', 'can see informe interventoria dispac')),
            },
        ),
        migrations.CreateModel(
            name='Contrato_Desembolso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requisito', models.CharField(max_length=250)),
                ('porcentaje', models.FloatField()),
                ('valor_requerido', models.FloatField()),
            ],
            options={
                'db_table': 'contrato_desembolso',
            },
        ),
        migrations.CreateModel(
            name='Contrato_Financiacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.IntegerField()),
                ('fecha_suscripcion', models.DateField()),
                ('es_cofinanciacion', models.BooleanField(default=False)),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empresa.Empresa')),
                ('tipo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tipo.Tipo')),
            ],
            options={
                'db_table': 'contrato_financiacion',
            },
        ),
        migrations.CreateModel(
            name='Contrato_Remuneracion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requisito', models.CharField(max_length=250)),
                ('porcentaje', models.FloatField()),
                ('valor_requerido', models.FloatField()),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
            ],
            options={
                'db_table': 'contrato_remuneracion',
            },
        ),
        migrations.CreateModel(
            name='VigenciaContrato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=4000)),
                ('fecha_inicio', models.DateField(blank=True, null=True)),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('valor', models.FloatField()),
                ('soporte', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('contrato', 'cto'))),
                ('acta_id', models.IntegerField(blank=True, null=True)),
                ('acta_compra', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('contrato', 'act_com'))),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tipo.Tipo')),
            ],
            options={
                'db_table': 'contrato_vigencia',
            },
        ),
        migrations.CreateModel(
            name='Sub_contratista',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('soporte', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('contrato', 'sub_cto'))),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_contrato_sub_contratista', to='contrato.Contrato')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_sub_contratista_empresa', to='empresa.Empresa')),
            ],
            options={
                'db_table': 'contrato_sub_contratista',
            },
        ),
        migrations.CreateModel(
            name='Rubro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=4000)),
                ('contrato', models.ManyToManyField(blank=True, related_name='fk_contrato_rubro', to='contrato.Contrato')),
            ],
            options={
                'db_table': 'contrato_rubro',
            },
        ),
        migrations.CreateModel(
            name='Contrato_Vigencia_anual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField()),
                ('porcentaje', models.FloatField()),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
            ],
            options={
                'db_table': 'contrato_vigencia_anual',
            },
        ),
        migrations.CreateModel(
            name='Contrato_Remuneracion_pagos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_pagado', models.FloatField()),
                ('fecha_suscripcion', models.DateField()),
                ('remuneracion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato_Remuneracion')),
            ],
            options={
                'db_table': 'contrato_remuneracion_pagos',
            },
        ),
        migrations.CreateModel(
            name='Contrato_financiacion_condicion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condicion', models.CharField(max_length=4000)),
                ('fecha_suscripcion', models.DateField()),
                ('financiacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato_Financiacion')),
            ],
            options={
                'db_table': 'contrato_financiacion_condicion',
            },
        ),
        migrations.CreateModel(
            name='Contrato_Desembolso_desembolsados',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_desembolsado', models.FloatField()),
                ('fecha_suscripcion', models.DateField()),
                ('desembolso', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato_Desembolso')),
            ],
            options={
                'db_table': 'contrato_desembolso_desembolsado',
            },
        ),
        migrations.AddField(
            model_name='contrato_desembolso',
            name='vigencia_anual',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato_Vigencia_anual'),
        ),
        migrations.CreateModel(
            name='Contrato_cesion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(blank=True, null=True)),
                ('soporte', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('contrato', 'cto_cs'))),
                ('contratista_antiguo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_cesion_contrato_empresa_antiguo', to='empresa.Empresa')),
                ('contratista_nuevo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_cesion_contrato_empresa_nuevo', to='empresa.Empresa')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_cesion_contrato', to='contrato.Contrato')),
            ],
            options={
                'db_table': 'contrato_cesion',
            },
        ),
        migrations.CreateModel(
            name='Contrato_CDP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(blank=True, null=True)),
                ('numero', models.CharField(max_length=50)),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
            ],
            options={
                'db_table': 'contrato_cdp',
            },
        ),
        migrations.CreateModel(
            name='ActaAsignacionRecursosContrato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actaAsignacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.ActaAsignacionRecursos')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
            ],
            options={
                'db_table': 'contrato_actaasignacionrecursoscontrato',
            },
        ),
        migrations.CreateModel(
            name='VigenciaContrato_motivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motivo', models.CharField(max_length=4000)),
                ('vigencia_contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.VigenciaContrato')),
            ],
            options={
                'db_table': 'contrato_vigencia_motivo',
                'unique_together': {('vigencia_contrato',)},
            },
        ),
        migrations.CreateModel(
            name='EmpresaContrato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participa', models.BooleanField(default=False)),
                ('edita', models.BooleanField(default=False)),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empresa.Empresa')),
            ],
            options={
                'db_table': 'contrato_empresa',
                'unique_together': {('contrato', 'empresa')},
            },
        ),
        migrations.CreateModel(
            name='Contrato_supervisor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cargo', models.IntegerField(choices=[(1, 'Principal'), (2, 'Apoyo')], default=1)),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empresa.Empresa')),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parametrizacion.Funcionario')),
            ],
            options={
                'db_table': 'contrato_supervisor',
                'unique_together': {('contrato', 'empresa', 'cargo')},
            },
        ),
        migrations.CreateModel(
            name='Contrato_Administracion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
            ],
            options={
                'db_table': 'contrato_administracion',
                'unique_together': {('contrato',)},
            },
        ),
        migrations.CreateModel(
            name='Contrato_Actividad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.CharField(max_length=4000)),
                ('actividad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Actividad')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
            ],
            options={
                'db_table': 'contrato_actividad_contrato',
                'unique_together': {('contrato', 'actividad')},
            },
        ),
        migrations.CreateModel(
            name='Cesion_economica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(blank=True, null=True)),
                ('soporte', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('contrato', 'cs_ecm'))),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_cesion_economica_contrato', to='contrato.Contrato')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_cesion_economica_empresa', to='empresa.Empresa')),
            ],
            options={
                'db_table': 'contrato_cesion_economica',
                'unique_together': {('contrato', 'empresa')},
            },
        ),
    ]
