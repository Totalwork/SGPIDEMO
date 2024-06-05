from tipo.models import Tipo
from estado.models import Estado

class TipoDocumento():
	app='poliza_tipo_documento'
	Giro = 1
	VigenciaContrato = 2
	OtroSi = 3

	def __init__(self):
		tipo=Tipo()
		self.Giro = tipo.ObtenerID(self.app,self.Giro)
		self.VigenciaContrato = tipo.ObtenerID(self.app,self.VigenciaContrato)
		self.OtroSi = tipo.ObtenerID(self.app,self.OtroSi)

class TipoActa():
	app='poliza_tipo_acta'
	Ninguno = 7
	ActaReinicio = 6
	ActaSuspension = 5
	ActaLiquidacion = 4

	def __init__(self):
		tipo=Tipo()
		self.Ninguno = tipo.ObtenerID(self.app, self.Ninguno)
		self.ActaReinicio = tipo.ObtenerID(self.app, self.ActaReinicio)
		self.ActaSuspension = tipo.ObtenerID(self.app, self.ActaSuspension)
		self.ActaLiquidacion = tipo.ObtenerID(self.app, self.ActaLiquidacion)
