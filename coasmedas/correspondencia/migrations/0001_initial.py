# Generated by Django 2.2.10 on 2023-01-20 22:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contrato', '0001_initial'),
        ('proyecto', '0001_initial'),
        ('usuario', '0001_initial'),
        ('empresa', '0001_initial'),
        ('parametrizacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CorresPfijo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250)),
                ('estado', models.BooleanField(default=True)),
                ('mostrar_ano', models.BooleanField(default=False)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaConsecutivo_empresa_Empresa', to='empresa.Empresa')),
            ],
            options={
                'permissions': (('can_see_CorresPfijo', 'can_see_CorresPfijo'),),
                'unique_together': {('nombre', 'empresa')},
            },
        ),
        migrations.CreateModel(
            name='CorrespondenciaEnviada',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consecutivo', models.BigIntegerField(blank=True)),
                ('fechaEnvio', models.DateField()),
                ('anoEnvio', models.BigIntegerField()),
                ('asunto', models.CharField(blank=True, max_length=4000)),
                ('referencia', models.CharField(blank=True, max_length=4000)),
                ('fechaRegistro', models.DateTimeField(auto_now_add=True)),
                ('grupoSinin', models.BooleanField(default=False)),
                ('persona_destino', models.CharField(blank=True, max_length=250)),
                ('cargo_persona', models.CharField(blank=True, max_length=250)),
                ('direccion', models.CharField(blank=True, max_length=250)),
                ('telefono', models.CharField(blank=True, max_length=250)),
                ('contenido', models.TextField(blank=True)),
                ('contenidoHtml', models.TextField(blank=True)),
                ('clausula_afectada', models.TextField(blank=True)),
                ('clausula_afectadaHtml', models.TextField(blank=True)),
                ('privado', models.BooleanField(default=False)),
                ('empresa_destino', models.CharField(blank=True, max_length=250)),
                ('anulado', models.BooleanField(default=False)),
                ('ciudad', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaEnviada_ciudad', to='parametrizacion.Municipio')),
                ('contrato', models.ManyToManyField(blank=True, related_name='fk_CorrespondenciaEnviada_contrato', to='contrato.Contrato')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaEnviada_empresa_Empresa', to='empresa.Empresa')),
                ('firma', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaEnviada_firma', to='parametrizacion.Funcionario')),
                ('municipioEmpresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaEnviada_municipioEmpresa', to='parametrizacion.Municipio')),
                ('prefijo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaEnviada_perfijo', to='correspondencia.CorresPfijo')),
                ('proyecto', models.ManyToManyField(blank=True, related_name='fk_CorrespondenciaEnviada_proyecto', to='proyecto.Proyecto')),
                ('usuario', models.ManyToManyField(related_name='fk_CorrespondenciaEnviada_usuario', to='usuario.Usuario')),
                ('usuarioSolicitante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaEnviada_usuarioSolicitante_Usuario', to='usuario.Usuario')),
            ],
            options={
                'permissions': (('can_see_CorrespondenciaEnviada', 'can_see_CorrespondenciaEnviada'),),
                'unique_together': {('empresa', 'consecutivo', 'anoEnvio', 'prefijo')},
            },
        ),
        migrations.CreateModel(
            name='CorrespondenciaSoporte',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=600, null=True)),
                ('soporte', models.FileField(null=True, upload_to='correspondencia')),
                ('anulado', models.BooleanField(default=False)),
                ('correspondencia', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaSoporte_correspondencia', to='correspondencia.CorrespondenciaEnviada')),
            ],
            options={
                'permissions': (('can_see_CorrespondenciaSoporte', 'can_see_CorrespondenciaSoporte'),),
            },
        ),
        migrations.CreateModel(
            name='CorrespondenciaPlantilla',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('soporte', models.FileField(null=True, upload_to='plantillas/correspondenciaEnviada')),
                ('empresa', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaPlantilla_empresa', to='empresa.Empresa')),
            ],
        ),
        migrations.CreateModel(
            name='CorrespondenciaRadicado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField()),
                ('numero', models.IntegerField()),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaRadicado_empresa', to='empresa.Empresa')),
            ],
            options={
                'unique_together': {('empresa', 'ano')},
            },
        ),
        migrations.CreateModel(
            name='CorrespondenciaConsecutivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField()),
                ('numero', models.IntegerField()),
                ('prefijo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_CorrespondenciaConsecutivo_CorresPfijo', to='correspondencia.CorresPfijo')),
            ],
            options={
                'permissions': (('can_see_CorrespondenciaConsecutivo', 'can_see_CorrespondenciaConsecutivo'),),
                'unique_together': {('prefijo', 'ano')},
            },
        ),
    ]
