from estado.models import Estado


class EstadoMulta():
	app='multa'
	solicitada = 1
	generada = 2
	notificada_contratista = 3
	apelada = 4
	confirmada = 5
	exonerada = 6
	modificada = 7
	anulada = 8
	elaborada = 9
	contabilizada = 10
	pendiente_contabilizacion = 11
	preconfirmadas = 12

	def __init__(self):  
		estado = Estado()
		self.solicitada = estado.ObtenerID(self.app,self.solicitada)
		self.generada = estado.ObtenerID(self.app,self.generada)
		self.notificada_contratista = estado.ObtenerID(self.app,self.notificada_contratista)
		self.apelada = estado.ObtenerID(self.app,self.apelada)
		self.confirmada = estado.ObtenerID(self.app,self.confirmada)
		self.exonerada = estado.ObtenerID(self.app,self.exonerada)
		self.modificada = estado.ObtenerID(self.app,self.modificada)
		self.anulada = estado.ObtenerID(self.app,self.anulada)
		self.elaborada = estado.ObtenerID(self.app,self.elaborada)
		self.contabilizada = estado.ObtenerID(self.app,self.contabilizada)
		self.pendiente_contabilizacion = estado.ObtenerID(self.app,self.pendiente_contabilizacion)
		self.preconfirmadas = estado.ObtenerID(self.app,self.preconfirmadas)


class Notificaciones():
	app='notificacion'

	multas_notificadas_contratista_plazo_por_vencer_o_vencido = 25
	multas_confirmadas_o_modificadas_sin_registro_of = 26
	multas_pendientes_por_contabilizar = 34
	multas_solicitud_actualizacion_de_estados = 38 # notificacion cuando se hace una solicitud o actualizacion de la multa
	multas_pre_confirmadas = 42
