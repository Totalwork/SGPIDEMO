from estado.models import Estado

class EstadoFondo():
	app='Gestion_proyecto_fondo'
	activo = 1
	inactivo = 2

	def __init__(self):  
	 	estado = Estado()
	 	self.activo = estado.ObtenerID(self.app,self.activo)
	 	self.inactivo = estado.ObtenerID(self.app,self.inactivo)