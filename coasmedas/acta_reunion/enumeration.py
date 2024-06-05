from estado.models import Estado
from tipo.models import Tipo

from django.conf import settings

class estadoA():
	app = 'acta_reunion'
	pausada = 155
	anulada = 156
	en_curso = 157
	cerrada = 158

	def __init__(self):
		estado = Estado()
		self.pausada = estado.ObtenerID(self.app,self.pausada)
		self.anulada = estado.ObtenerID(self.app,self.anulada)
		self.en_curso = estado.ObtenerID(self.app,self.en_curso)
		self.cerrada = estado.ObtenerID(self.app,self.cerrada)
		

class tipoAH():
	app = 'acta_reunion_historial'
	creacion= 121
	sesion_control= 122
	anulacion= 123
	cerrar = 133
	dar_curso = 134
	# cerrar = 129
	# dar_curso = 130

	def __init__(self):
		tipo = Tipo()
		self.creacion = tipo.ObtenerID(self.app,self.creacion)
		self.sesion_control = tipo.ObtenerID(self.app,self.sesion_control)
		self.anulacion = tipo.ObtenerID(self.app,self.anulacion)
		self.cerrar = tipo.ObtenerID(self.app,self.cerrar)
		self.dar_curso = tipo.ObtenerID(self.app,self.dar_curso)

class estadoC():
	app = 'compromiso'
	por_cumplir= 159
	por_vencer= 160
	vencido= 161
	cumplido= 162
	cumplido_despues_vencido= 163
	cancelado=164

	def __init__(self):
		estado = Estado()
		self.por_cumplir = estado.ObtenerID(self.app,self.por_cumplir)
		self.por_vencer = estado.ObtenerID(self.app,self.por_vencer)
		self.vencido = estado.ObtenerID(self.app,self.vencido)
		self.cumplido = estado.ObtenerID(self.app,self.cumplido)
		self.cumplido_despues_vencido = estado.ObtenerID(self.app,self.cumplido_despues_vencido)
		self.cancelado = estado.ObtenerID(self.app,self.cancelado)

class tipoCH():
	app = 'compromiso_historial'	
	creacion=124
	proroga=125
	cancelacion=126
	resignacion=127
	cumplimiento=128
	restablecer=135
	# restablecer=131
	def __init__(self):
		tipo = Tipo()
		self.creacion = tipo.ObtenerID(self.app,self.creacion)
		self.proroga = tipo.ObtenerID(self.app,self.proroga)
		self.cancelacion = tipo.ObtenerID(self.app,self.cancelacion)
		self.resignacion = tipo.ObtenerID(self.app,self.resignacion)
		self.cumplimiento = tipo.ObtenerID(self.app,self.cumplimiento)
