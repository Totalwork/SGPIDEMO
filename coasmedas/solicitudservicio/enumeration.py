from tipo.models import Tipo
from estado.models import Estado


class TipoT():
	app='SolicitudServicio'
	OtroSi = 2
	Contrato = 1

	def __init__(self): 
		tipo=Tipo()
		self.OtroSi = tipo.ObtenerID(self.app,self.OtroSi)
		self.Contrato = tipo.ObtenerID(self.app,self.Contrato)


class EstadoT():
	app='SolicitudServicio'
	Terminado = 3
	EnTramite = 2
	Solicitado = 1	

	def __init__(self):  
		estado = Estado()
		self.Terminado = estado.ObtenerID(self.app,self.Terminado)
		self.EnTramite = estado.ObtenerID(self.app,self.EnTramite)
		self.Solicitado = estado.ObtenerID(self.app,self.Solicitado)	 	