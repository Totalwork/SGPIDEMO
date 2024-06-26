# Generated by Django 2.2.10 on 2023-01-20 22:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('proyecto', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PuntosGps',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=1000)),
                ('longitud', models.CharField(max_length=50)),
                ('latitud', models.CharField(max_length=50)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fk_Proyecto_proyecto', to='proyecto.Proyecto')),
            ],
            options={
                'db_table': 'puntos_gps',
                'permissions': (('can_see_puntosgps', 'can_see_puntosgps'), ('can_see_cargaMasiva', 'can_see_cargaMasiva')),
            },
        ),
    ]
