from tipo.models import Tipo
from estado.models import Estado

class TipoT():
	app='Tarea'
	grupo = 2
	propia = 1

	def __init__(self): 
	 	tipo=Tipo()
	 	self.grupo = tipo.ObtenerID(self.app,self.grupo)
	 	self.propia = tipo.ObtenerID(self.app,self.propia)

class EstadoT():
	app='Tarea'
	solicitada = 1
	no_leida = 2
	leida = 3
	atendida_fueraTiempo = 4
	atendida = 5
	por_vencer = 6
	reasignada = 7
	vencida = 8
	cancelada = 9
	rechazada = 10

	def __init__(self):  
	 	estado = Estado()
	 	self.solicitada = estado.ObtenerID(self.app,self.solicitada)
	 	self.no_leida = estado.ObtenerID(self.app,self.no_leida)
	 	self.leida = estado.ObtenerID(self.app,self.leida)
	 	self.atendida_fueraTiempo = estado.ObtenerID(self.app,self.atendida_fueraTiempo)
	 	self.atendida = estado.ObtenerID(self.app,self.atendida)
	 	self.por_vencer = estado.ObtenerID(self.app,self.por_vencer)
	 	self.reasignada = estado.ObtenerID(self.app,self.reasignada)
	 	self.vencida = estado.ObtenerID(self.app,self.vencida)
	 	self.cancelada = estado.ObtenerID(self.app,self.cancelada)
	 	self.rechazada = estado.ObtenerID(self.app,self.rechazada)