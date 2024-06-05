from estado.models import Estado

# Local
# class estadoFactura():
# 	activa = 2002
# 	anulada = 2003
# 	compensada = 2004

# class tablaForanea():
# 	encabezadoGiros = 20
# 	factura = 1086
# 	cesion = 1088
# 	descuento = 1089

# class notificacion():
# 	cod = 1

# Maquina Virtual
class estadoFactura():
	estado = Estado()
	app = 'Factura'

	activa = estado.ObtenerID(app,52)
	anulada = estado.ObtenerID(app,53)
	compensada = estado.ObtenerID(app,54)

# class estadoFactura():
# 	app = 'Factura'
# 	activa = 52
# 	anulada = 53
# 	compensada = 54

# 	def __init__(self):
# 		estado = Estado()
# 		self.activa = estado.ObtenerID(self.app,self.activa)
# 		self.anulada = estado.ObtenerID(self.app,self.anulada)
# 		self.compensada = estado.ObtenerID(self.app,self.compensada)

class tablaForanea():
	encabezadoGiros = 38
	factura = 140
	cesion = 142
	descuento = 143
	multa = 161

class notificacion():
	cod = 27
	sinTestOp = 46
	sinCodigoCompensacion = 47
		