from django.db import models
from empresa.models import Empresa
from tipo.models import Tipo
from contrato.models import Contrato
from proyecto.models import Proyecto
from usuario.models import Usuario
# Create your models here.
class BaseModel(models.Model):
 nombre = models.CharField(max_length=250)

 class Meta:
   abstract = True

 def __unicode__(self):
  return self.nombre

class Archivo(BaseModel):
	padre = models.IntegerField(blank=True)
	destino = models.FileField(upload_to='mi_nube',blank=True, null=True)
	tipoArchivo = models.ForeignKey(Tipo , related_name = 'fk_Tipo_Archivo' , on_delete=models.PROTECT)
	eliminado = models.BooleanField(default=False)
	peso = models.FloatField(blank=True)
	propietario = models.ForeignKey(Usuario , related_name="fk_Archivo_propietario" , on_delete=models.PROTECT)
	fechaModificado = models.DateTimeField(auto_now_add=True) 
	usuarioModificado = models.ForeignKey(Usuario , related_name="fk_usuarioModificado_Archivo" , on_delete=models.PROTECT)
	contrato  = models.ManyToManyField(Contrato, related_name='fk_Contrato_Archivo' , blank=True)
	proyecto  = models.ManyToManyField(Proyecto, related_name='fk_Proyecto_Archivo' , blank=True)

	class Meta:
		unique_together = (("padre", "nombre" , "tipoArchivo" , "propietario"),)
		permissions = (("can_see_Archivo","can_see_Archivo"),)

class ArchivoUsuario(models.Model):	
	usuario = models.ForeignKey(Usuario , related_name="fk_Usuario_ArchivoUsuario" , on_delete=models.PROTECT)
	archivo = models.ForeignKey(Archivo , related_name="fk_Archivo_ArchivoUsuario" , on_delete=models.PROTECT)#tipos de movimientos en la cuenta
	escritura = models.BooleanField(default=False)

	class Meta:
		unique_together = ( ("usuario", "archivo" ), )
		permissions = (("can_see_ArchivoUsuario","can_see_ArchivoUsuario"),)

	
