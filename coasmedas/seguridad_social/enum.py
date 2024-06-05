from estado.models import Estado

class EnumEstadoPlanilla():
	AlDia='Al dia'
	Vencida='Vencida'
	PagadoFueraFecha='Pagado Fuera de Fecha'
	PorVencer='Por Vencer'

class EnumEstadoEmpleado():
	app = 'seguridad_social'
	Ingreso=0
	Retiro=0
	ReIngreso=0
	def __init__(self):		
		estados = Estado.objects.filter(app=self.app)
		for item in estados:
			if item.codigo==1:
				self.Ingreso=item.id	
			if item.codigo==2:
				self.ReIngreso=item.id	
			if item.codigo==3:
				self.Retiro=item.id		
				