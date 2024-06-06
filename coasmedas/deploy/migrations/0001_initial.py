# Generated by Django 2.2.10 on 2023-01-30 15:29

from django.db import migrations, models
import django.db.models.deletion
import coasmedas.functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NombreArchivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150)),
            ],
            options={
                'db_table': 'deploy_nombre_archivo',
            },
        ),
        migrations.CreateModel(
            name='SistemaVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(max_length=100, unique=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('activo', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'deploy_sistema_version',
            },
        ),
        migrations.CreateModel(
            name='ZInformacionArchivos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('deploy'))),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('nombre_archivo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_sistema_version_nombre_archivo', to='deploy.NombreArchivo')),
                ('sistema_version', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_sistema_version_informacion_archivo', to='deploy.SistemaVersion')),
            ],
            options={
                'db_table': 'deploy_informacion_archivos',
            },
        ),
    ]
