from django.db import models

from coasmedas.functions import functions, RandomFileName

from proyecto.models import Proyecto
from usuario.models import Usuario
from estado.models import Estado
from tipo.models import Tipo

# Create your models here.
class NoConformidad(models.Model):
    limit_valoracion =    models.Q(app='no_conformidad_valoracion')
    limit_tipo =    models.Q(app='no_conformidad')
    proyecto = models.ForeignKey(Proyecto, related_name='fk_no_conformidad_proyecto', on_delete=models.PROTECT)
    usuario = models.ForeignKey(Usuario, related_name='fk_no_conformidad_usuario', on_delete=models.PROTECT)
    estado = models.ForeignKey(Estado, related_name='fk_no_conformidad_estado', on_delete=models.PROTECT)
    detectada = models.ForeignKey(Usuario, related_name='fk_no_conformidad_detectada_usuario', on_delete=models.PROTECT)
    descripcion_no_corregida = models.CharField(max_length=4000)
    descripcion_corregida = models.CharField(max_length=4000, blank=True, null=True)
    foto_no_corregida = models.ImageField(upload_to = RandomFileName('no_conformidad/foto_no_corregida','no_cf_no_crr'), blank=True, null=True)
    foto_no_corregida2 = models.ImageField(upload_to = RandomFileName('no_conformidad/foto_no_corregida','no_cf_no_crr'), blank=True, null=True)
    foto_no_corregida3 = models.ImageField(upload_to = RandomFileName('no_conformidad/foto_no_corregida','no_cf_no_crr'), blank=True, null=True)
    # foto_no_corregida = models.ImageField(upload_to = 'no_conformidad/foto_no_corregida')
    foto_corregida = models.ImageField(upload_to = RandomFileName('no_conformidad/foto_corregida','no_cf_crr'), blank=True, null=True)
    foto_corregida2 = models.ImageField(upload_to = RandomFileName('no_conformidad/foto_corregida','no_cf_crr'), blank=True, null=True)
    foto_corregida3 = models.ImageField(upload_to = RandomFileName('no_conformidad/foto_corregida','no_cf_crr'), blank=True, null=True)
    # foto_corregida = models.ImageField(upload_to = 'no_conformidad/foto_corregida', blank=True, null=True)
    fecha_no_corregida = models.DateField(blank=True, null=True)
    fecha_corregida = models.DateField(blank=True, null=True)
    terminada = models.BooleanField(default=False)
    estructura = models.CharField(max_length=1000)
    primer_correo = models.DateField(blank=True, null=True)
    segundo_correo = models.DateField(blank=True, null=True)
    tercer_correo = models.DateField(blank=True, null=True)
    valoracion = models.ForeignKey(Tipo, related_name='fk_no_conformidad_valoracion', on_delete=models.PROTECT, 
                                limit_choices_to=limit_valoracion, null=True, blank=True)
    tipo = models.ForeignKey(Tipo, related_name='fk_no_conformidad_tipo', on_delete=models.PROTECT,
                            limit_choices_to=limit_tipo, null=True, blank=True)
   
    class Meta:
        db_table = 'no_conformidad'
        permissions = (("can_see_no_conformidad","can see no_conformidad"),)

    def __str__(self):
        return self.descripcion_no_corregida

    @property   
    def foto_no_corregida_publica(self):
        if self.foto_no_corregida:           
            return functions.crearRutaTemporalArchivoS3(str(self.foto_no_corregida))
        else:
            return None 
            
    @property   
    def foto_corregida_publica(self):
        if self.foto_corregida:           
            return functions.crearRutaTemporalArchivoS3(str(self.foto_corregida))
        else:
            return None

    @property   
    def foto_no_corregida2_publica(self):
        if self.foto_no_corregida2:           
            return functions.crearRutaTemporalArchivoS3(str(self.foto_no_corregida2))
        else:
            return None 

    @property   
    def foto_no_corregida3_publica(self):
        if self.foto_no_corregida3:           
            return functions.crearRutaTemporalArchivoS3(str(self.foto_no_corregida3))
        else:
            return None  
            
    @property   
    def foto_corregida_publica(self):
        if self.foto_corregida:           
            return functions.crearRutaTemporalArchivoS3(str(self.foto_corregida))
        else:
            return None  

    @property   
    def foto_corregida2_publica(self):
        if self.foto_corregida2:           
            return functions.crearRutaTemporalArchivoS3(str(self.foto_corregida2))
        else:
            return None  

    @property   
    def foto_corregida3_publica(self):
        if self.foto_corregida3:           
            return functions.crearRutaTemporalArchivoS3(str(self.foto_corregida3))
        else:
            return None   