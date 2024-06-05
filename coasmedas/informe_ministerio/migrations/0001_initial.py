# Generated by Django 2.2.10 on 2023-01-30 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tipo', '0001_initial'),
        ('empresa', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Planilla',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(blank=True, null=True, upload_to='informe_ministerio')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='planilla_empresa', to='empresa.Empresa')),
                ('tipo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='planilla_tipo', to='tipo.Tipo')),
            ],
            options={
                'db_table': 'informe_planilla',
                'permissions': (('can_see_planilla', 'can see planilla'),),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('modelo', models.CharField(blank=True, max_length=250, null=True)),
                ('campo', models.CharField(blank=True, max_length=250, null=True)),
                ('tag_especial', models.BooleanField(default=False)),
                ('mayuscula', models.BooleanField(default=False)),
                ('nombre_variable', models.CharField(blank=True, max_length=250, null=True)),
                ('inner', models.TextField(blank=True, null=True)),
                ('planilla', models.ManyToManyField(blank=True, related_name='tag_planilla', to='informe_ministerio.Planilla')),
            ],
            options={
                'db_table': 'informe_tag',
                'permissions': (('can_see_tag', 'can see tag'),),
            },
        ),
    ]