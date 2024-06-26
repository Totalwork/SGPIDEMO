# Generated by Django 2.2.10 on 2023-01-30 15:28

from django.db import migrations, models
import django.db.models.deletion
import coasmedas.functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('seguimiento_factura', '0001_initial'),
        ('estado', '0001_initial'),
        ('empresa', '0001_initial'),
        ('parametrizacion', '0001_initial'),
        ('proyecto', '0001_initial'),
        ('proceso', '0001_initial'),
        ('contrato', '0001_initial'),
        ('tipo', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Compensacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referencia', models.CharField(blank=True, max_length=500)),
                ('fecha', models.DateField()),
                ('descripcion', models.CharField(blank=True, max_length=4000, null=True)),
                ('valor', models.FloatField()),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_compensacion_contrato', to='contrato.Contrato')),
            ],
            options={
                'db_table': 'factura_compensacion',
            },
        ),
        migrations.CreateModel(
            name='Factura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referencia', models.CharField(blank=True, max_length=500)),
                ('numero', models.CharField(max_length=100)),
                ('radicado', models.CharField(blank=True, max_length=500)),
                ('fecha', models.DateField(blank=True, null=True)),
                ('concepto', models.CharField(max_length=4000)),
                ('valor_factura', models.FloatField()),
                ('valor_contable', models.FloatField(blank=True, null=True)),
                ('valor_subtotal', models.FloatField(blank=True, null=True)),
                ('soporte', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('factura/factura', 'fac'))),
                ('pagada', models.BooleanField(default=False)),
                ('bloqueo_factura', models.BooleanField(default=False)),
                ('recursos_propios', models.BooleanField(default=False)),
                ('orden_pago', models.BooleanField(default=False)),
                ('fecha_reporte', models.DateField(blank=True, null=True)),
                ('fecha_pago', models.DateField(blank=True, null=True)),
                ('motivo_anulacion', models.TextField(blank=True, null=True)),
                ('fecha_contabilizacion', models.DateField(blank=True, null=True)),
                ('fecha_vencimiento', models.DateField(blank=True, null=True)),
                ('codigo_op', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_seguimiento_factura', to='seguimiento_factura.GestionOp')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_factura_contrato', to='contrato.Contrato')),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_factura_estado', to='estado.Estado')),
                ('mcontrato', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_factura_mcontrato', to='contrato.Contrato')),
                ('proceso_soporte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_factura_soporte_proceso', to='proceso.HSoporteProcesoRelacionDato')),
            ],
            options={
                'db_table': 'factura',
                'permissions': (('can_see_factura', 'can see factura'), ('can_see_deshabilitarFactura', 'can_see_deshabilitarFactura'), ('can_see_habilitarFactura', 'can_see_habilitarFactura'), ('can_see_cargaMasivaFactura', 'can_see_cargaMasivaFactura'), ('can_see_facturas_por_contabilizar', 'can see facturas por contabilizar')),
            },
        ),
        migrations.CreateModel(
            name='MesCausado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mes', models.CharField(max_length=20)),
                ('ano', models.CharField(max_length=10)),
                ('factura', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_mesCausado_factura', to='factura.Factura')),
            ],
            options={
                'db_table': 'factura_mes_causado',
            },
        ),
        migrations.CreateModel(
            name='DetalleCompensacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_registro', models.IntegerField()),
                ('compensacion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_detalleCompensacion_compensacion', to='factura.Compensacion')),
                ('tablaForanea', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_tablaForanea_detalleCompensacion', to='contenttypes.ContentType', verbose_name='Tabla foranea del DetalleCompensacion')),
            ],
            options={
                'db_table': 'factura_detalle_compensacion',
            },
        ),
        migrations.CreateModel(
            name='Descuento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referencia', models.CharField(blank=True, max_length=500)),
                ('numero_cuenta', models.CharField(blank=True, max_length=500, null=True)),
                ('concepto', models.CharField(max_length=4000)),
                ('valor', models.FloatField()),
                ('soporte', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('factura/descuento', 'fac_desc'))),
                ('banco', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_descuento_banco', to='parametrizacion.Banco')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_descuento_contrato', to='contrato.Contrato')),
            ],
            options={
                'db_table': 'factura_descuento',
            },
        ),
        migrations.CreateModel(
            name='Cesion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referencia', models.CharField(blank=True, max_length=500)),
                ('numero_cuenta', models.CharField(blank=True, max_length=500, null=True)),
                ('descripcion', models.CharField(blank=True, max_length=4000, null=True)),
                ('fecha', models.DateField(blank=True, null=True)),
                ('valor', models.FloatField()),
                ('soporte', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('factura/cesion', 'fac_ces'))),
                ('banco', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_cesion_banco', to='parametrizacion.Banco')),
                ('beneficiario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_cesion_beneficiario', to='empresa.Empresa')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_cesion_contrato2', to='contrato.Contrato')),
                ('proceso_soporte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_cesion_soporte_proceso', to='proceso.HSoporteProcesoRelacionDato')),
                ('tipo_cuenta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cesion_tipoCuenta', to='tipo.Tipo')),
            ],
            options={
                'db_table': 'factura_cesion',
            },
        ),
        migrations.CreateModel(
            name='FacturaProyecto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.FloatField(blank=True, null=True)),
                ('factura', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_factura_facturaProyecto', to='factura.Factura')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_proyecto_facturaProyecto', to='proyecto.Proyecto')),
            ],
            options={
                'db_table': 'factura_proyecto',
                'unique_together': {('factura', 'proyecto')},
            },
        ),
    ]
