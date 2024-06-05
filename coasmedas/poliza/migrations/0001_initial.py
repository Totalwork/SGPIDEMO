# Generated by Django 2.2.10 on 2023-01-20 22:36

from django.db import migrations, models
import django.db.models.deletion
import sinin4.functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contrato', '0001_initial'),
        ('tipo', '0001_initial'),
        ('estado', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aseguradora',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'poliza_aseguradora',
                'permissions': (('can_see_aseguradora', 'can see aseguradora'),),
            },
        ),
        migrations.CreateModel(
            name='Poliza',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contrato', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='poliza_contrato', to='contrato.Contrato')),
                ('estado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='poliza_estado', to='estado.Estado')),
                ('tipo', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='poliza_tipo_poliza', to='tipo.Tipo')),
            ],
            options={
                'db_table': 'poliza',
                'permissions': (('can_see_poliza', 'can see poliza'),),
            },
        ),
        migrations.CreateModel(
            name='VigenciaPoliza',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField(null=True)),
                ('fecha_final', models.DateField(null=True)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=18, null=True)),
                ('observacion', models.TextField(null=True)),
                ('soporte', models.FileField(blank=True, null=True, upload_to=sinin4.functions.RandomFileName('poliza/soporte', 'plz'))),
                ('amparo', models.CharField(max_length=500, null=True)),
                ('tomador', models.CharField(max_length=100, null=True)),
                ('numero', models.CharField(max_length=200, null=True)),
                ('reemplaza', models.BooleanField(default=False)),
                ('documento_id', models.IntegerField(blank=True, null=True)),
                ('numero_certificado', models.CharField(blank=True, max_length=300, null=True)),
                ('aseguradora', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vigencia_poliza_aseguradora', to='poliza.Aseguradora')),
                ('poliza', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vigencia_poliza_tipo_poliza', to='poliza.Poliza')),
                ('tipo_acta', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='poliza_tipo_acta', to='tipo.Tipo')),
                ('tipo_documento', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='poliza_tipo_documento', to='tipo.Tipo')),
            ],
            options={
                'db_table': 'poliza_vigencia_poliza',
                'ordering': ['id'],
                'permissions': (('can_see_vigencia_poliza', 'can see vigencia poliza'),),
            },
        ),
        migrations.CreateModel(
            name='ZBeneficiorio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120)),
                ('vigencia_poliza', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vigencia_poliza_beneficiario', to='poliza.VigenciaPoliza')),
            ],
            options={
                'db_table': 'poliza_beneficiario_vigencia_poliza',
                'permissions': (('can_see_vigencia_poliza_beneficiario_vigencia_poliza', 'can see beneficiario vigencia poliza'),),
            },
        ),
        migrations.CreateModel(
            name='VigenciaPoliza_AprobacionMME',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(blank=True, null=True)),
                ('vigencia_poliza', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='poliza.VigenciaPoliza')),
            ],
            options={
                'db_table': 'poliza_vigencia_poliza_aprobacion_mme',
                'unique_together': {('vigencia_poliza',)},
            },
        ),
    ]
