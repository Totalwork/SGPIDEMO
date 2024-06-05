from estado.models import Estado
from tipo.models import Tipo

class enumEstados():
	app='EstadoControlCambio'
	Pendiente = 1
	Aprovada = 2
	Rechazado = 3

	def __init__(self):  
		estado = Estado()
		self.Pendiente = estado.ObtenerID(self.app,self.Pendiente)
		self.Aprovada = estado.ObtenerID(self.app,self.Aprovada)
		self.Rechazado = estado.ObtenerID(self.app,self.Rechazado)


class enumTipo():
	app='control_cambios'
	Replanteo = 2
	Cambio = 3
	Definitivo = 4

	def __init__(self):  
		tipo = Tipo()
		self.Replanteo = tipo.ObtenerID(self.app,self.Replanteo)
		self.Cambio = tipo.ObtenerID(self.app,self.Cambio)
		self.Definitivo = tipo.ObtenerID(self.app,self.Definitivo)