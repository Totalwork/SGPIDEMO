# Generated by Django 2.2.10 on 2023-01-20 22:32

from django.db import migrations, models
import django.db.models.deletion
import coasmedas.functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('empresa', '0001_initial'),
        ('usuario', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banco',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('codigo_bancario', models.IntegerField()),
            ],
            options={
                'permissions': (('puede_ver', 'puede ver'),),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('firma_cartas', models.BooleanField(default=False)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='empresa.Empresa')),
            ],
            options={
                'permissions': (('can_see_cargo', 'can see cargo'),),
            },
        ),
        migrations.CreateModel(
            name='Departamento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('iniciales', models.CharField(max_length=50)),
            ],
            options={
                'permissions': (('puede_ver', 'puede ver'),),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EResponsabilidades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='responsabilidades_empresa', to='empresa.Empresa')),
            ],
            options={
                'db_table': 'parametrizacion_responsabilidad',
            },
        ),
        migrations.CreateModel(
            name='GrupoVideosTutoriales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('orden', models.IntegerField(default=0)),
            ],
            options={
                'permissions': (('can_see_grupo_videos_tutoriales', 'can see grupo videos tutoriales'),),
            },
        ),
        migrations.CreateModel(
            name='VideosTutoriales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255)),
                ('poster', models.ImageField(blank=True, null=True, upload_to=coasmedas.functions.RandomFileName('video_tutorial', ''), verbose_name='Poster del video')),
                ('video', models.FileField(upload_to=coasmedas.functions.RandomFileName('video_tutorial', ''), verbose_name='Video')),
                ('orden', models.IntegerField(default=0)),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parametrizacion.GrupoVideosTutoriales')),
            ],
            options={
                'permissions': (('can_see_videos_tutoriales', 'can see videos tutoriales'),),
            },
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=150, null=True, unique=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('tabla_referencia', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fk_tablaReferenciaNotificacion', to='contenttypes.ContentType', verbose_name='Tabla Referenciada')),
                ('usuario_cc', models.ManyToManyField(blank=True, related_name='fk_notificacion_usuario', to='usuario.Persona')),
            ],
            options={
                'db_table': 'parametrizacion_notificacion',
                'permissions': (('can_see_notificacion', 'can see notificacion'),),
            },
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('departamento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='parametrizacion.Departamento')),
            ],
            options={
                'permissions': (('puede_ver', 'puede ver'),),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iniciales', models.CharField(blank=True, max_length=20, null=True)),
                ('activo', models.BooleanField(default=True)),
                ('cargo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cargo_funcionario', to='parametrizacion.Cargo')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='empresa_funcionario', to='empresa.Empresa')),
                ('notificaciones', models.ManyToManyField(blank=True, related_name='fk_funcionario_notificacion', to='parametrizacion.Notificacion')),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='persona_funcionario', to='usuario.Persona')),
                ('responsabilidades', models.ManyToManyField(related_name='fk_funcionario_responsabilidades', to='parametrizacion.EResponsabilidades')),
            ],
            options={
                'permissions': (('can_see_funcionario', 'can see funcionario'),),
            },
        ),
    ]
