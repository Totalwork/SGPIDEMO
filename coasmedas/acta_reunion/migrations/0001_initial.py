# Generated by Django 2.2.10 on 2023-01-30 15:34

from django.db import migrations, models
import django.db.models.deletion
import coasmedas.functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('empresa', '0001_initial'),
        ('usuario', '0001_initial'),
        ('tipo', '0001_initial'),
        ('proyecto', '0001_initial'),
        ('contrato', '0001_initial'),
        ('estado', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consecutivo', models.IntegerField()),
                ('tema_principal', models.CharField(max_length=2000)),
                ('soporte', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('acta_reunion/acta', 'act'))),
                ('conclusiones', models.CharField(blank=True, max_length=2000, null=True)),
                ('fecha', models.DateField()),
                ('tiene_contrato', models.BooleanField(default=True)),
                ('tiene_proyecto', models.BooleanField(default=True)),
                ('tiene_conclusiones', models.BooleanField(default=True)),
                ('tiene_compromisos', models.BooleanField(default=True)),
                ('acta_previa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='acta_reunion.Acta')),
                ('contrato', models.ManyToManyField(blank=True, related_name='fk_contrato_acta', to='contrato.Contrato')),
                ('controlador_actual', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_controlador_acta', to='usuario.Usuario')),
                ('estado', models.ForeignKey(blank=True, default=155, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_estado_acta', to='estado.Estado')),
                ('proyecto', models.ManyToManyField(blank=True, related_name='fk_proyecto_acta', to='proyecto.Proyecto')),
                ('usuario_organizador', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_organizador_acta', to='usuario.Usuario')),
            ],
            options={
                'db_table': 'acta_acta',
                'permissions': (('can_see_acta', 'can_see_acta'),),
            },
        ),
        migrations.CreateModel(
            name='Compromiso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('responsable_interno', models.BooleanField(default=False)),
                ('fecha_compromiso', models.DateField()),
                ('fecha_proximidad', models.DateField()),
                ('descripcion', models.CharField(max_length=2000)),
                ('requiere_soporte', models.BooleanField(default=False)),
                ('soporte', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('acta_reunion/compromiso', 'com'))),
                ('notificar_organizador', models.BooleanField(default=True)),
                ('notificar_controlador', models.BooleanField(default=True)),
                ('acta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_acta_acta_compromiso', to='acta_reunion.Acta')),
                ('estado', models.ForeignKey(default=159, on_delete=django.db.models.deletion.PROTECT, related_name='fk_estado_compromiso', to='estado.Estado')),
            ],
            options={
                'db_table': 'acta_compromiso',
                'permissions': (('can_see_acta_compromiso', 'can_see_acta_compromiso'),),
            },
        ),
        migrations.CreateModel(
            name='Tema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tema', models.CharField(max_length=2000)),
                ('acta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_acta_tema', to='acta_reunion.Acta')),
            ],
            options={
                'db_table': 'acta_tema',
                'permissions': (('can_see_tema', 'can_see_tema'),),
            },
        ),
        migrations.CreateModel(
            name='Participante_interno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asistio', models.BooleanField(default=False)),
                ('acta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_acta_participante_interno', to='acta_reunion.Acta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_usuario_participante_interno', to='usuario.Usuario')),
            ],
            options={
                'db_table': 'acta_participante_interno',
                'permissions': (('can_see_participante_interno', 'can_see_participante_interno'),),
            },
        ),
        migrations.CreateModel(
            name='Participante_externo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asistio', models.BooleanField(default=False)),
                ('acta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_acta_participante_externo', to='acta_reunion.Acta')),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_persona_participante_externo', to='usuario.Persona')),
            ],
            options={
                'db_table': 'acta_participante_externo',
                'permissions': (('can_see_participante_externo', 'can_see_participante_externo'),),
            },
        ),
        migrations.CreateModel(
            name='Compromiso_historial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('motivo', models.CharField(blank=True, max_length=2000, null=True)),
                ('compromiso', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_compromiso_compromiso_historial', to='acta_reunion.Compromiso')),
                ('participante_externo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_participante_externo_compromiso_historial', to='acta_reunion.Participante_externo')),
                ('participante_interno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_participante_interno_compromiso_historial', to='acta_reunion.Participante_interno')),
                ('tipo_operacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_tipo_compromiso_historial', to='tipo.Tipo')),
            ],
            options={
                'db_table': 'acta_compromiso_historial',
                'permissions': (('can_see_compromiso_historial', 'can_see_compromiso_historial'),),
            },
        ),
        migrations.AddField(
            model_name='compromiso',
            name='participante_responsable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_participante_responsable_compromiso', to='acta_reunion.Participante_externo'),
        ),
        migrations.AddField(
            model_name='compromiso',
            name='supervisor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_supervisor_compromiso', to='usuario.Usuario'),
        ),
        migrations.AddField(
            model_name='compromiso',
            name='usuario_responsable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_usuario_responsable_compromiso', to='usuario.Usuario'),
        ),
        migrations.CreateModel(
            name='Acta_historial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('motivo', models.CharField(blank=True, max_length=2000, null=True)),
                ('acta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_acta_acta_historial', to='acta_reunion.Acta')),
                ('controlador', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_controlador_acta_historial', to='usuario.Usuario')),
                ('tipo_operacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_tipo_acta_historial', to='tipo.Tipo')),
            ],
            options={
                'db_table': 'acta_acta_historial',
                'permissions': (('can_see_acta_historial', 'can_see_acta_historial'),),
            },
        ),
        migrations.CreateModel(
            name='Consecutivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField()),
                ('consecutivo', models.IntegerField()),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_empresa_consecutivo', to='empresa.Empresa')),
            ],
            options={
                'db_table': 'acta_consecutivo',
                'permissions': (('can_see_consecutivo', 'can_see_consecutivo'),),
                'unique_together': {('empresa', 'ano')},
            },
        ),
    ]
