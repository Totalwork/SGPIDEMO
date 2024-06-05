from estado.models import Estado
from tipo.models import Tipo

es=Estado()

class enumEstados():

	solicitado = es.ObtenerID('EstadoGiro',1)
	autorizado = es.ObtenerID('EstadoGiro',2)
	pagado = es.ObtenerID('EstadoGiro',3)
	rechazado =es.ObtenerID('EstadoGiro',4)
	reversado =es.ObtenerID('EstadoGiro',5)


ti=Tipo()

class enumTipo():

	egreso = ti.ObtenerID('TipoFinacieroCuentaMovimiento',1)
	ingreso = ti.ObtenerID('TipoFinacieroCuentaMovimiento',2)
	ingreso_rendimiento = ti.ObtenerID('TipoFinacieroCuentaMovimiento',3)


tipoPagoAnticipo=Tipo()

# origen donde se paga el anticipo
class enumTipoPagoAnticipo():

	cuenta_bancaria = tipoPagoAnticipo.ObtenerID('encabezadoGiro_pago_recurso',1)
	recursos_propios = tipoPagoAnticipo.ObtenerID('encabezadoGiro_pago_recurso',2)
	recursos_propios_transicional = tipoPagoAnticipo.ObtenerID('encabezadoGiro_pago_recurso',3)
