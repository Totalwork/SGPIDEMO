# Generated by Django 2.2.10 on 2023-01-30 15:29

from django.db import migrations, models
import django.db.models.deletion
import sinin4.functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contrato', '0001_initial'),
        ('estado', '0001_initial'),
        ('tipo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ASolicitud',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(blank=True, null=True)),
                ('observacion', models.CharField(blank=True, max_length=4000, null=True)),
                ('carta_aceptacion', models.FileField(blank=True, null=True, upload_to=sinin4.functions.RandomFileName('solicitud/solicitud', 'slt_crt'))),
                ('soporte', models.FileField(blank=True, null=True, upload_to=sinin4.functions.RandomFileName('solicitud/solicitud', 'slt_spt'))),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='estado.Estado')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tipo.Tipo')),
            ],
            options={
                'db_table': 'solicitud',
                'permissions': (('can_see_solicitud', 'can see solicitud'),),
            },
        ),
        migrations.CreateModel(
            name='BRequisitoCompras',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'solicitud_requisito_compras',
            },
        ),
        migrations.CreateModel(
            name='BRequisitoJuridico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'solicitud_requisito_juridico',
            },
        ),
        migrations.CreateModel(
            name='BRequisitoPoliza',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'solicitud_requisito_poliza',
            },
        ),
        migrations.CreateModel(
            name='BRequisitoTecnico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=1000)),
            ],
            options={
                'db_table': 'solicitud_requisito_tecnico',
            },
        ),
        migrations.CreateModel(
            name='CFavorabilidadCompras',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacion', models.CharField(blank=True, max_length=4000, null=True)),
                ('soporte', models.FileField(blank=True, null=True, upload_to=sinin4.functions.RandomFileName('solicitud/favorabilidad_compras', 'fvd_cmp'))),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='solicitud.ASolicitud')),
            ],
            options={
                'db_table': 'solicitud_favorabilidad_compras',
            },
        ),
        migrations.CreateModel(
            name='CFavorabilidadJuridica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacion', models.CharField(blank=True, max_length=4000, null=True)),
                ('soporte', models.FileField(blank=True, null=True, upload_to=sinin4.functions.RandomFileName('solicitud/favorabilidad_juridica', 'fvd_jrc'))),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='solicitud.ASolicitud')),
            ],
            options={
                'db_table': 'solicitud_favorabilidad_juridica',
            },
        ),
        migrations.CreateModel(
            name='CFavorabilidadTecnica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacion', models.CharField(blank=True, max_length=4000, null=True)),
                ('soporte', models.FileField(blank=True, null=True, upload_to=sinin4.functions.RandomFileName('solicitud/favorabilidad_tecnica', 'fvd_tcn'))),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='solicitud.ASolicitud')),
            ],
            options={
                'db_table': 'solicitud_favorabilidad_tecnica',
            },
        ),
        migrations.CreateModel(
            name='CValidarPoliza',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('soporte', models.FileField(blank=True, null=True, upload_to=sinin4.functions.RandomFileName('solicitud/validar_poliza', 'vld_plz'))),
                ('solicitud', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_validar_poliza_solicitud', to='solicitud.ASolicitud')),
            ],
            options={
                'db_table': 'solicitud_validar_poliza',
            },
        ),
        migrations.CreateModel(
            name='DPolizaTipo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tipo.Tipo')),
                ('validar_poliza', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_poliza_tipo_validar_poliza', to='solicitud.CValidarPoliza')),
            ],
            options={
                'db_table': 'solicitud_poliza_tipo',
            },
        ),
        migrations.CreateModel(
            name='EPolizaTipoRequisito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.BooleanField(default=False)),
                ('poliza_tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_poliza_tipo_requisito_tipo', to='solicitud.DPolizaTipo')),
                ('requisito', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_poliza_tipo_requisito_requisito', to='solicitud.BRequisitoPoliza')),
            ],
            options={
                'db_table': 'solicitud_poliza_tipo_requisito',
            },
        ),
        migrations.CreateModel(
            name='DFavorabilidadTecnicaRequisito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.BooleanField(default=False)),
                ('favorabilidad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='solicitud.CFavorabilidadTecnica')),
                ('requisito', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='solicitud.BRequisitoTecnico')),
            ],
            options={
                'db_table': 'solicitud_favorabilidad_tecnica_requisito',
            },
        ),
        migrations.CreateModel(
            name='DFavorabilidadJuridicaRequisito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.BooleanField(default=False)),
                ('favorabilidad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='solicitud.CFavorabilidadJuridica')),
                ('requisito', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_favorabilidad_juridica_requisito', to='solicitud.BRequisitoJuridico')),
            ],
            options={
                'db_table': 'solicitud_favorabilidad_juridica_requisito',
            },
        ),
        migrations.CreateModel(
            name='DFavorabilidadComprasRequisito',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.BooleanField(default=False)),
                ('favorabilidad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='solicitud.CFavorabilidadCompras')),
                ('requisito', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='solicitud.BRequisitoCompras')),
            ],
            options={
                'db_table': 'solicitud_favorabilidad_compras_requisito',
            },
        ),
    ]
