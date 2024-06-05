# from tipo.models import Tipo
from estado.models import Estado
from tipo.models import Tipo

from django.conf import settings

#Defino mi clase base
class BaseEntity(object):
	app = 'contrato'
	# estado = Estado()
	# tipo = Tipo()

class tipoC(BaseEntity):
	contratoProyecto = 8
	interventoria = 9
	medida = 10
	retie = 11
	m_contrato = 12
	suministros = 13
	obra = 14
	otros = 15

	def __init__(self):
		tipo = Tipo()
		self.contratoProyecto = tipo.ObtenerID(self.app,self.contratoProyecto)
		self.interventoria = tipo.ObtenerID(self.app,self.interventoria)
		self.medida = tipo.ObtenerID(self.app,self.medida)
		self.retie = tipo.ObtenerID(self.app,self.retie)
		self.m_contrato = tipo.ObtenerID(self.app,self.m_contrato)
		self.suministros = tipo.ObtenerID(self.app,self.suministros)
		self.obra = tipo.ObtenerID(self.app,self.obra)
		self.otros = tipo.ObtenerID(self.app,self.otros)

class tipoV():
	app = 'vigenciaContrato'
	contrato= 16
	otrosi = 17
	actaSuspension = 18
	actaReinicio = 19
	replanteo = 20
	liquidacion = 21
	actaInicio = 22
	actaAmpliacion = 23
	actaRecepcion = 24
	actaCesion = 120

	def __init__(self):
		tipo = Tipo()
		self.contrato = tipo.ObtenerID(self.app,self.contrato)
		self.otrosi = tipo.ObtenerID(self.app,self.otrosi)
		self.actaSuspension = tipo.ObtenerID(self.app,self.actaSuspension)
		self.actaReinicio = tipo.ObtenerID(self.app,self.actaReinicio)
		self.replanteo = tipo.ObtenerID(self.app,self.replanteo)
		self.liquidacion = tipo.ObtenerID(self.app,self.liquidacion)
		self.actaInicio = tipo.ObtenerID(self.app,self.actaInicio)
		self.actaAmpliacion = tipo.ObtenerID(self.app,self.actaAmpliacion)
		self.actaRecepcion = tipo.ObtenerID(self.app,self.actaRecepcion)

# Defino mis estados
class estadoC(BaseEntity):
	vigente = 28
	liquidado = 29
	suspendido = 30
	porVencer = 31
	vencido = 32

	def __init__(self):
		estado = Estado()
		self.vigente = estado.ObtenerID(self.app,self.vigente)
		self.liquidado = estado.ObtenerID(self.app,self.liquidado)
		self.suspendido = estado.ObtenerID(self.app,self.suspendido)
		self.porVencer = estado.ObtenerID(self.app,self.porVencer)
		self.vencido = estado.ObtenerID(self.app,self.vencido)

class notificacion():
	# Para Enelar
	db = settings.DATABASES['default']['NAME']
	if db == 'sinin41_Enelar':
		cod = 3
	else:
		cod = 6
		aux = 11
		ic = 50