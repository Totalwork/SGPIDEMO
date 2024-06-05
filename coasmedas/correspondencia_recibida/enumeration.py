from estado.models import Estado
from tipo.models import Tipo

#Defino mi clase base
class BaseEntity(object):
	app = 'correspondencia_recibida'

class Notificaciones():
	app='notificacion'

	cartas_recibidas_sin_revisar = 1
	cartas_recibidas_sin_cargar_soporte = 2
	correspondencia_recibida_sin_responder = 13


# Defino mis estados
class correspondenciaRecibidaEstados(BaseEntity):
	por_Revisar = 0
	revisada = 1
	respondida = 3
	reasignada = 4
	anulada = 5

	def __init__(self):
		estado = Estado()
		self.por_Revisar = estado.ObtenerID(self.app,self.por_Revisar)
		self.revisada = estado.ObtenerID(self.app,self.revisada)
		self.respondida = estado.ObtenerID(self.app,self.respondida)
		self.reasignada = estado.ObtenerID(self.app,self.reasignada)
		self.anulada = estado.ObtenerID(self.app,self.anulada)
