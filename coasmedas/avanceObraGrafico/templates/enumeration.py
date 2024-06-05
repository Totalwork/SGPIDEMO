from tipo.models import Tipo
from estado.models import Estado

class TipoT():
	app='AvanceObraGrafico'
	crear = 1
	eliminar = 2
	modificar_cantidad = 3

	def __init__(self): 
	 	tipo=Tipo()
	 	self.crear = tipo.ObtenerID(self.app,self.crear)
	 	self.eliminar = tipo.ObtenerID(self.app,self.eliminar)
	 	self.modificar_cantidad = tipo.ObtenerID(self.app,self.modificar_cantidad)

# class EstadoT():
# 	app='AvanceObraGrafico'
# 	solicitada = 1
# 	no_leida = 2

# 	def __init__(self):  
# 	 	estado = Estado()
# 	 	self.solicitada = estado.ObtenerID(self.app,self.solicitada)
# 	 	self.no_leida = estado.ObtenerID(self.app,self.no_leida)