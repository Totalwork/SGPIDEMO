from estado.models import Estado

es=Estado()

class enumEstados():

	tramite = es.ObtenerID('CesionEconomica',1)
	aprobacion = es.ObtenerID('CesionEconomica',2)
	aprobada = es.ObtenerID('CesionEconomica',3)
	anulada = es.ObtenerID('CesionEconomica',4)
	rechazado = es.ObtenerID('CesionEconomica',5)
	pagado = es.ObtenerID('CesionEconomica',6)

