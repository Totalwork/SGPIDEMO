from django.db import models
from parametrizacion.models import Municipio  , Banco ,  Funcionario
from empresa.models import Empresa
from contrato.models import Contrato
from tipo.models import Tipo 
from estado.models import Estado

#Create your models here.
class BaseModel(models.Model):
	nombre = models.TextField()

	class Meta:
		abstract = True
	def __unicode__(self):
		return self.nombre
# FONDOS DEL PROYECTO
class P_fondo(BaseModel):
	descripcion = models.CharField(max_length = 250)
	
	def __unicode__(self):
		return self.nombre


#TIPOS DEL PROYECTO
class P_tipo(BaseModel):
	fondo_proyecto = models.ForeignKey(P_fondo , on_delete=models.PROTECT)	

class Proyecto(BaseModel):
	municipio = models.ForeignKey(Municipio , related_name = 'f_Municipio_parametrizacion' , on_delete=models.PROTECT)
	No_cuenta = models.CharField(max_length=50 , blank=True)
	entidad_bancaria = models.ForeignKey(Banco , related_name = 'f_Banco_parametrizacion' , on_delete=models.PROTECT , null = True , blank = True)										  
	tipo_cuenta= models.ForeignKey(Tipo , related_name = 'f_Tipo_cuenta' , on_delete=models.PROTECT , null = True , blank = True)#related_name="f_MODEL_APP"
	estado_proyecto = models.ForeignKey(Estado , related_name = 'f_Estado_proyecto_estado' , on_delete=models.PROTECT )
	valor_adjudicado = models.FloatField()	
	tipo_proyecto = models.ForeignKey(P_tipo , related_name = 'f_P_tipo_proyecto' , on_delete=models.PROTECT)
	fecha_inicio = 	models.DateField(null = True , blank = True) 	
	fecha_fin = models.DateField(null = True , blank = True)
	contrato  = models.ManyToManyField(Contrato, related_name='fk_contrato')
	funcionario  = models.ManyToManyField(Funcionario, related_name='fk_proyecto_funcionario')#responsables del proyecto
	mcontrato = models.ForeignKey(Contrato, related_name = 'f_Contrato_contrato' , on_delete=models.PROTECT , default=1843)

	class Meta:
		ordering=['nombre']
		unique_together = (("nombre" , "municipio"),)
		permissions = (("can_see_Proyecto","can_see_Proyecto"),("Can_see_informe","Can see informe"))

class Proyecto_historial_estado(models.Model):
	comentarios = models.CharField(max_length = 1000)
	fecha = models.DateField()
	fecha_transacion = models.DateTimeField(auto_now_add=True)
	estado_proyecto = models.ForeignKey(Estado , related_name = 'fk_proyecto_historial_Estado_proyecto_estado' , on_delete=models.PROTECT)#related_name="f_MODEL_MODEL_APP"
	proyecto = models.ForeignKey(Proyecto , related_name = "fk_proyecto_historial_Proyecto_proyecto" , on_delete=models.PROTECT)

class Proyecto_empresas(models.Model):
	proyecto = models.ForeignKey(Proyecto , related_name = 'fk_proyecto_empresa_proyecto' , on_delete=models.PROTECT)
	empresa = models.ForeignKey(Empresa , related_name = 'fk_proyecto_empresa_empresa' , on_delete=models.PROTECT)
	propietario = models.BooleanField(default=False)
	class Meta:
		unique_together = (("proyecto", "empresa"), )
		permissions = (("can_see_ProyectoEmpresa","can_see_ProyectoEmpresa"),)


class Proyecto_campo_info_tecnica(BaseModel):
	tipo_proyecto = models.ForeignKey(P_tipo , related_name = 'f_P_tipo_proyecto_campo_infotecnica' , blank = True , on_delete=models.PROTECT)
	unidad_medida = models.CharField(max_length=10)
	class Meta:
		unique_together = ("tipo_proyecto", "nombre")

class Proyecto_info_tecnica(models.Model):
	proyecto = models.ForeignKey(Proyecto , on_delete=models.PROTECT)							
	campo = models.ForeignKey(Proyecto_campo_info_tecnica, related_name = "f_Proyecto_modelo_info_tecnica_proyecto" , on_delete=models.PROTECT)#related_name="f_MODEL_APP"
	valor_diseno = models.FloatField()
	valor_replanteo = models.FloatField(null = True )
	valor_ejecucion = models.FloatField(null = True )
	class Meta:
		unique_together = (("proyecto", "campo"),)
		permissions = (("can_see_ProyectoInfoTecnica","ProyectoInfoTecnica"),)

class Contrato_fondo(models.Model):
	fondo = models.ForeignKey(P_fondo, on_delete=models.PROTECT)
	contrato = models.ForeignKey(Contrato, on_delete=models.PROTECT)
	class Meta:
		db_table = 'proyecto_contrato_fondo'
		unique_together=('contrato','fondo')		

class Proyecto_actividad(models.Model):
	proyecto = models.ForeignKey(Proyecto, related_name='fk_actividad_proyecto', on_delete=models.PROTECT)
	descripcion = models.CharField(max_length=4000, blank=True, null=True)
	fecha = models.DateField(blank=True, null=True)

	class Meta:
		db_table = 'proyecto_actividad'

class Proyecto_proyecto_codigo(models.Model):
	proyecto 	= models.ForeignKey(Proyecto , on_delete=models.PROTECT)
	codigo 		= models.CharField(max_length = 250)

	class Meta:
		db_table = 'proyecto_proyecto_codigo'
		unique_together = [
			["proyecto",],
 		]