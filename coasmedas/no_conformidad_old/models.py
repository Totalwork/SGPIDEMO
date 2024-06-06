from django.db import models

from coasmedas.functions import functions

from proyecto.models import Proyecto
from usuario.models import Usuario
from estado.models import Estado

# Create your models here.
class NoConformidad(models.Model):
    proyecto = models.ForeignKey(Proyecto, related_name='fk_no_conformidad_proyecto', on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, related_name='fk_no_conformidad_usuario', on_delete=models.PROTECT)
    estado = models.ForeignKey(Estado, related_name='fk_no_conformidad_estado', on_delete=models.PROTECT)
    detectada = models.ForeignKey(Usuario, related_name='fk_no_conformidad_detectada_usuario', on_delete=models.PROTECT)
    descripcion_no_corregida = models.CharField(max_length=4000)
    descripcion_corregida = models.CharField(max_length=4000, blank=True, null=True)
    foto_no_corregida = models.ImageField(upload_to = functions.path_and_rename('no_conformidad/foto_no_corregida','no_cf_no_crr'), blank=True, null=True)
    # foto_no_corregida = models.ImageField(upload_to = 'no_conformidad/foto_no_corregida')
    foto_corregida = models.ImageField(upload_to = functions.path_and_rename('no_conformidad/foto_corregida','no_cf_crr'), blank=True, null=True)
    # foto_corregida = models.ImageField(upload_to = 'no_conformidad/foto_corregida', blank=True, null=True)
    fecha_no_corregida = models.DateField(blank=True, null=True)
    fecha_corregida = models.DateField(blank=True, null=True)
    terminada = models.BooleanField(default=False)
    estructura = models.CharField(max_length=1000)
    primer_correo = models.DateField(blank=True, null=True)
    segundo_correo = models.DateField(blank=True, null=True)
    tercer_correo = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'no_conformidad'
        permissions = (("can_see_no_conformidad","can see no_conformidad"),)

    def __unicode__(self):
        return self.descripcion_no_corregida