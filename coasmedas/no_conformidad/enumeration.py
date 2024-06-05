from estado.models import Estado

class estadoNoConformidad():
	estado = Estado()
	app = 'No_conformidad'

	corregida = estado.ObtenerID(app,2)
	sin_corregir = estado.ObtenerID(app,1)


class tipoNoConformidad(object):
	#tipo = Tipo()
	app = 'no_conformidad'

	tecnica = 129
	admin = 130

class valoracionNoConformidad(object):
	#tipo = Tipo()
	app = 'no_conformidad_valoracion'

	mayor = 131
	menor = 132
