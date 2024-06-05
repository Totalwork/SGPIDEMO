from estado.models import Estado

es=Estado()

class enumEstados():

	en_verificacon = es.ObtenerID('CesionV2',1)
	en_tramite = es.ObtenerID('CesionV2',2)
	aprobada = es.ObtenerID('CesionV2',3)
	rechazada = es.ObtenerID('CesionV2',4)
	aprobada_parcialmente = es.ObtenerID('CesionV2',5)

