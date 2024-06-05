# Generated by Django 2.2.10 on 2023-01-20 22:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tipo', '0001_initial'),
        ('estado', '0001_initial'),
        ('contrato', '0001_initial'),
        ('parametrizacion', '0001_initial'),
        ('empresa', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='P_fondo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
                ('descripcion', models.CharField(max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='P_tipo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
                ('fondo_proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='proyecto.P_fondo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
                ('No_cuenta', models.CharField(blank=True, max_length=50)),
                ('valor_adjudicado', models.FloatField()),
                ('fecha_inicio', models.DateField(blank=True, null=True)),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('contrato', models.ManyToManyField(related_name='fk_contrato', to='contrato.Contrato')),
                ('entidad_bancaria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='f_Banco_parametrizacion', to='parametrizacion.Banco')),
                ('estado_proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='f_Estado_proyecto_estado', to='estado.Estado')),
                ('funcionario', models.ManyToManyField(related_name='fk_proyecto_funcionario', to='parametrizacion.Funcionario')),
                ('mcontrato', models.ForeignKey(default=1843, on_delete=django.db.models.deletion.PROTECT, related_name='f_Contrato_contrato', to='contrato.Contrato')),
                ('municipio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='f_Municipio_parametrizacion', to='parametrizacion.Municipio')),
                ('tipo_cuenta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='f_Tipo_cuenta', to='tipo.Tipo')),
                ('tipo_proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='f_P_tipo_proyecto', to='proyecto.P_tipo')),
            ],
            options={
                'ordering': ['nombre'],
                'permissions': (('can_see_Proyecto', 'can_see_Proyecto'), ('Can_see_informe', 'Can see informe')),
                'unique_together': {('nombre', 'municipio')},
            },
        ),
        migrations.CreateModel(
            name='Proyecto_campo_info_tecnica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField()),
                ('unidad_medida', models.CharField(max_length=10)),
                ('tipo_proyecto', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='f_P_tipo_proyecto_campo_infotecnica', to='proyecto.P_tipo')),
            ],
            options={
                'unique_together': {('tipo_proyecto', 'nombre')},
            },
        ),
        migrations.CreateModel(
            name='Proyecto_historial_estado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentarios', models.CharField(max_length=1000)),
                ('fecha', models.DateField()),
                ('fecha_transacion', models.DateTimeField(auto_now_add=True)),
                ('estado_proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_proyecto_historial_Estado_proyecto_estado', to='estado.Estado')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_proyecto_historial_Proyecto_proyecto', to='proyecto.Proyecto')),
            ],
        ),
        migrations.CreateModel(
            name='Proyecto_actividad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(blank=True, max_length=4000, null=True)),
                ('fecha', models.DateField(blank=True, null=True)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_actividad_proyecto', to='proyecto.Proyecto')),
            ],
            options={
                'db_table': 'proyecto_actividad',
            },
        ),
        migrations.CreateModel(
            name='Proyecto_proyecto_codigo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=250)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='proyecto.Proyecto')),
            ],
            options={
                'db_table': 'proyecto_proyecto_codigo',
                'unique_together': {('proyecto',)},
            },
        ),
        migrations.CreateModel(
            name='Proyecto_info_tecnica',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor_diseno', models.FloatField()),
                ('valor_replanteo', models.FloatField(null=True)),
                ('valor_ejecucion', models.FloatField(null=True)),
                ('campo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='f_Proyecto_modelo_info_tecnica_proyecto', to='proyecto.Proyecto_campo_info_tecnica')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='proyecto.Proyecto')),
            ],
            options={
                'permissions': (('can_see_ProyectoInfoTecnica', 'ProyectoInfoTecnica'),),
                'unique_together': {('proyecto', 'campo')},
            },
        ),
        migrations.CreateModel(
            name='Proyecto_empresas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('propietario', models.BooleanField(default=False)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_proyecto_empresa_empresa', to='empresa.Empresa')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_proyecto_empresa_proyecto', to='proyecto.Proyecto')),
            ],
            options={
                'permissions': (('can_see_ProyectoEmpresa', 'can_see_ProyectoEmpresa'),),
                'unique_together': {('proyecto', 'empresa')},
            },
        ),
        migrations.CreateModel(
            name='Contrato_fondo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contrato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contrato.Contrato')),
                ('fondo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='proyecto.P_fondo')),
            ],
            options={
                'db_table': 'proyecto_contrato_fondo',
                'unique_together': {('contrato', 'fondo')},
            },
        ),
    ]
