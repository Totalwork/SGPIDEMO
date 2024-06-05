# Generated by Django 2.2.10 on 2023-01-30 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contrato', '0001_initial'),
        ('proyecto', '0001_initial'),
        ('usuario', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='APeriodicidadG',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('numero_dias', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Periodicidad',
                'db_table': 'avanceObraLite_periodicidad',
                'permissions': (('can_see_periodicidadlite', 'can see periodicidadlite'),),
                'unique_together': {('nombre',)},
            },
        ),
        migrations.CreateModel(
            name='BEsquemaCapitulosG',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('macrocontrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='esquema_macrocontrato', to='contrato.Contrato')),
            ],
            options={
                'verbose_name': 'Esquemas',
                'db_table': 'avanceObraLite_esquemaCapitulos',
                'permissions': (('can_see_esquemacapituloslite', 'can see esquemacapituloslite'),),
            },
        ),
        migrations.CreateModel(
            name='CatalogoUnidadConstructiva',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('ano', models.IntegerField()),
                ('activo', models.BooleanField(default=True)),
                ('mcontrato', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='catalogo_mcontrato', to='contrato.Contrato')),
            ],
            options={
                'verbose_name': 'Catalogo de Unidades Constructivas',
                'db_table': 'avanceObraLite_catalogo',
                'permissions': (('can_see_catalogo', 'can see catalogo'),),
            },
        ),
        migrations.CreateModel(
            name='CEsquemaCapitulosActividadesG',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('nivel', models.IntegerField()),
                ('padre', models.IntegerField()),
                ('peso', models.FloatField()),
                ('esquema', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='actividades_esquemalite', to='avanceObraLite.BEsquemaCapitulosG')),
            ],
            options={
                'verbose_name': 'Capitulos y actividades',
                'db_table': 'avanceObraLite_esquemaCapitulosActividades',
                'permissions': (('can_see_esquemacapitulosactividadeslite', 'can see esquemacapitulosactividadeslite'),),
            },
        ),
        migrations.CreateModel(
            name='Cronograma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('programacionCerrada', models.BooleanField(default=False)),
                ('fechaInicio', models.DateField(blank=True, null=True)),
                ('fechaFinal', models.DateField(blank=True, null=True)),
                ('confirmarFechas', models.BooleanField(default=False)),
                ('esquema', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cronograma_esquema_lite', to='avanceObraLite.BEsquemaCapitulosG')),
                ('periodicidad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cronograma_perioridicidad_lite', to='avanceObraLite.APeriodicidadG')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cronograma_proyecto_lite', to='proyecto.Proyecto')),
            ],
            options={
                'verbose_name': 'Cronograma',
                'db_table': 'avanceObraLite_cronograma',
                'permissions': (('can_see_cronograma', 'can see cronograma'),),
            },
        ),
        migrations.CreateModel(
            name='EPresupuesto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('cerrar_presupuesto', models.BooleanField(default=False)),
                ('aiu', models.FloatField()),
                ('cronograma', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='presupuesto_cronograma_lite', to='avanceObraLite.Cronograma')),
            ],
            options={
                'verbose_name': 'Encabezado de presupuesto',
                'db_table': 'avanceObraLite_presupuesto',
                'permissions': (('can_see_presupuesto', 'can see presupuesto'),),
            },
        ),
        migrations.CreateModel(
            name='PeriodoProgramacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaDesde', models.DateField(blank=True, null=True)),
                ('fechaHasta', models.DateField(blank=True, null=True)),
                ('cronograma', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='periodoProgramacion_cronograma', to='avanceObraLite.Cronograma')),
            ],
            options={
                'verbose_name': 'ProgramacionPeriodo',
                'db_table': 'avanceObraLite_periodoProgramacion',
                'permissions': (('can_see_periodoProgramacionPeriodo', 'can see periodoProgramacion'),),
            },
        ),
        migrations.CreateModel(
            name='TipoUnidadConstructiva',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('activa', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Tipo de unidad constructiva',
                'db_table': 'avanceObraLite_tipounidadconstructiva',
            },
        ),
        migrations.CreateModel(
            name='UnidadConstructiva',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20)),
                ('descripcion', models.CharField(max_length=200)),
                ('catalogo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='unidadConstructiva_catalogo', to='avanceObraLite.CatalogoUnidadConstructiva')),
                ('tipoUnidadConstructiva', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='unidadConstructiva_tipo', to='avanceObraLite.TipoUnidadConstructiva')),
            ],
            options={
                'verbose_name': 'Unidad constructiva',
                'db_table': 'avanceObraLite_unidadconstructiva',
            },
        ),
        migrations.CreateModel(
            name='ReporteTrabajo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaReporte', models.DateField()),
                ('sinAvance', models.BooleanField(default=False)),
                ('motivoSinAvance', models.CharField(blank=True, max_length=255, null=True)),
                ('reporteCerrado', models.BooleanField(default=False)),
                ('periodoProgramacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reporteTrabajo_periodoProgramacion', to='avanceObraLite.PeriodoProgramacion')),
                ('usuario_registro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reportetrabajo_usuario_lite', to='usuario.Usuario')),
            ],
            options={
                'verbose_name': 'ReporteTrabajo',
                'db_table': 'avanceObraLite_reporteTrabajo',
                'permissions': (('can_see_reporteTrabajo', 'can see reporteTrabajo'),),
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20)),
                ('descripcion', models.CharField(max_length=200)),
                ('valorUnitario', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True)),
                ('unidadMedida', models.CharField(default='Und', max_length=10)),
                ('catalogo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Material_catalogo', to='avanceObraLite.CatalogoUnidadConstructiva')),
            ],
            options={
                'verbose_name': 'Material',
                'db_table': 'avanceObraLite_material',
            },
        ),
        migrations.CreateModel(
            name='ManoDeObra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=20)),
                ('descripcion', models.CharField(max_length=200)),
                ('valorHora', models.DecimalField(decimal_places=2, max_digits=30)),
                ('catalogo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ManoDeObra_catalogo', to='avanceObraLite.CatalogoUnidadConstructiva')),
            ],
            options={
                'verbose_name': 'Mano de obra',
                'db_table': 'avanceObraLite_manodeobra',
            },
        ),
        migrations.CreateModel(
            name='FDetallePresupuesto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigoUC', models.CharField(blank=True, max_length=20, null=True)),
                ('descripcionUC', models.CharField(blank=True, max_length=255, null=True)),
                ('valorManoObra', models.DecimalField(blank=True, decimal_places=4, max_digits=30, null=True)),
                ('valorMaterial', models.DecimalField(blank=True, decimal_places=4, max_digits=30, null=True)),
                ('valorGlobal', models.DecimalField(blank=True, decimal_places=4, max_digits=30, null=True)),
                ('cantidad', models.DecimalField(blank=True, decimal_places=4, max_digits=30, null=True)),
                ('porcentaje', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True)),
                ('actividad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detallePresupuesto_esquemacpitulosactividades_lite', to='avanceObraLite.CEsquemaCapitulosActividadesG')),
                ('catalogoUnidadConstructiva', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detallePresupuesto_catalogoUnidadConstructiva', to='avanceObraLite.CatalogoUnidadConstructiva')),
                ('presupuesto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detallePresupuesto_presupuesto_lite', to='avanceObraLite.EPresupuesto')),
            ],
            options={
                'verbose_name': 'detalle de presupuesto',
                'db_table': 'avanceObraLite_detallePresupuesto',
                'permissions': (('can_see_detallepresupuesto', 'can see detallepresupuesto'),),
            },
        ),
        migrations.CreateModel(
            name='DetalleReporteTrabajo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(blank=True, decimal_places=4, max_digits=30, null=True)),
                ('detallePresupuesto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detalleReporteTrabajo_detallePresupuesto', to='avanceObraLite.FDetallePresupuesto')),
                ('reporteTrabajo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detalleReporteTrabajo_reporteTrabajo', to='avanceObraLite.ReporteTrabajo')),
            ],
            options={
                'verbose_name': 'DetalleReporteTrabajo',
                'db_table': 'avanceObraLite_detalleReporteTrabajo',
                'permissions': (('can_see_detalleReporteTrabajo', 'can see detalleReporteTrabajo'),),
            },
        ),
        migrations.CreateModel(
            name='DetallePeriodoProgramacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(blank=True, decimal_places=4, max_digits=30, null=True)),
                ('detallePresupuesto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detallePeriodoProgramacion_detallePresupuesto', to='avanceObraLite.FDetallePresupuesto')),
                ('periodoProgramacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detallePeriodoProgramacion_periodoProgramacion', to='avanceObraLite.PeriodoProgramacion')),
            ],
            options={
                'verbose_name': 'DetallePeriodoProgramacion',
                'db_table': 'avanceObraLite_detallePeriodoProgramacion',
                'permissions': (('can_see_detallePeriodoProgramacion', 'can see detallePeriodoProgramacion'),),
            },
        ),
        migrations.CreateModel(
            name='DesgloceMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=4, max_digits=30)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='desgloceMaterial_material', to='avanceObraLite.Material')),
                ('unidadConstructiva', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='desgloceMaterial_unidadConstructiva', to='avanceObraLite.UnidadConstructiva')),
            ],
            options={
                'verbose_name': 'Desgloce de material',
                'db_table': 'avanceObraLite_desglocematerial',
            },
        ),
        migrations.CreateModel(
            name='DesgloceManoDeObra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rendimiento', models.DecimalField(decimal_places=4, max_digits=30)),
                ('manoDeObra', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='desgloceManoDeObra_manoDeObra', to='avanceObraLite.ManoDeObra')),
                ('unidadConstructiva', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='desgloceManoDeObra_unidadConstructiva', to='avanceObraLite.UnidadConstructiva')),
            ],
            options={
                'verbose_name': 'Desgloce de mano de obra',
                'db_table': 'avanceObraLite_desglocemanodeobra',
            },
        ),
    ]
