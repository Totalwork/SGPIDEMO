from tipo.models import Tipo

class EnumTipoCorrespondecia():
	app = 'correspondencia'
	Radicado=0
	Consecutivo=0	
	def __init__(self):		
		tipos = Tipo.objects.filter(app=self.app)
		for item in tipos:
			if item.codigo==0:
				self.Radicado=item.id	
			if item.codigo==1:
				self.Consecutivo=item.id	

class Notificaciones():
	app='notificacion'

	cartas_enviadas_sin_cargar_soporte = 3