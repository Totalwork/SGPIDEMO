# Generated by Django 2.2.10 on 2023-01-30 15:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuario', '0001_initial'),
        ('proyecto', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bitacora',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentario', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True, null=True)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bitacora_proyecto', to='proyecto.Proyecto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bitacora_usuario', to='usuario.Usuario')),
            ],
            options={
                'permissions': (('can_see_bitacora', 'can see bitacora'), ('see_all_bitacora', 'see all bitacora')),
            },
        ),
    ]
