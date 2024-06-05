from estado.models import Estado

class estadoNoConformidad():
	estado = Estado()
	app = 'No_conformidad'

	corregida = estado.ObtenerID(app,2)
	sin_corregir = estado.ObtenerID(app,1)