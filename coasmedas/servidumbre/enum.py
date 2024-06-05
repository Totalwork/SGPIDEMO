from estado.models import Estado
from tipo.models import Tipo

es=Estado()

class enumEstados():

	abierto = es.ObtenerID('Servidumbre_expediente',159)
	cerrado = es.ObtenerID('Servidumbre_expediente',160)



ti=Tipo()

class enumTipo():

	finca = ti.ObtenerID('Servidumbre_predio',108)
	parcela = ti.ObtenerID('Servidumbre_predio',109)
	lote = ti.ObtenerID('Servidumbre_predio',110)



