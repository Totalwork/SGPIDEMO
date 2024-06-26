# Generated by Django 2.2.10 on 2023-01-20 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remitente', models.EmailField(max_length=254)),
                ('destinatario', models.TextField()),
                ('copia', models.TextField(blank=True, null=True)),
                ('asunto', models.CharField(max_length=255)),
                ('contenido', models.TextField()),
                ('tieneAdjunto', models.BooleanField(default=False)),
                ('adjunto', models.TextField(blank=True, null=True)),
                ('appLabel', models.CharField(max_length=100)),
                ('enviado', models.BooleanField(default=False)),
                ('horaPreparacion', models.DateTimeField(auto_now_add=True)),
                ('horaEnvio', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
