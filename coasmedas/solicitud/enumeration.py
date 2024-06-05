from estado.models import Estado
from tipo.models import Tipo

#Defino mi clase base
class BaseEntity(object):
	app = 'Solicitud'

class estadoSolicitud(BaseEntity):
	estado = Estado()
	app = 'Solicitud'

	enEstudio = estado.ObtenerID(app,1)
	aprobada = estado.ObtenerID(app,2)
	rechazada = estado.ObtenerID(app,3)