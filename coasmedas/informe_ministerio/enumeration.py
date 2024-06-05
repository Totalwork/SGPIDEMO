from tipo.models import Tipo

class TipoInforme():
	app='Informe_ministerio'
	informe_eca = 1

	def __init__(self):  
		tipo = Tipo()
		self.informe_eca = tipo.ObtenerID(self.app,self.informe_eca)