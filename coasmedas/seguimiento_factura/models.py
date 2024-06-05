from django.db import models
from empresa.models import Empresa
from contrato.models import Contrato
from financiero.models import FinancieroCuenta
from django.db.models import Count
from django.db.models import F, FloatField, Sum
from sinin4.functions import functions, RandomFileName
import datetime


class GestionOp(models.Model):

	# valor = models.FloatField()
	# beneficiario=models.ForeignKey(Empresa,related_name="seguimiento_factura_empresa",on_delete=models.PROTECT)
	codigo = models.CharField(max_length=100, unique=True)
	fecha_registro = models.DateField(auto_now_add=True, blank=True)
	fecha_pago = models.DateField(null=True,blank=True)
	#soporte = models.FileField(upload_to='seguimiento_factura/gestio_op',blank=True, null=True)
	soporte= models.FileField(upload_to = RandomFileName('seguimiento_factura/gestio_op','fac'), blank=True, null=True)
	# contrato=models.ForeignKey(Contrato,related_name="seguimiento_contrato",on_delete=models.PROTECT)
	pagado_recursos_propios = models.BooleanField(default=False)
	#soporte_pago = models.FileField(upload_to='seguimiento_factura/gestio_op',blank=True, null=True)
	soporte_pago= models.FileField(upload_to = RandomFileName('seguimiento_factura/gestio_op','soporte_pago'), blank=True, null=True)
	facturas_anuladas = models.TextField(blank=True)
	anulado = models.BooleanField(default = False)
	# def financiero_cuenta(self):
	# 	# cuenta=FinancieroCuenta.objects.filter(contrato__id=self.contrato.id).values('id','nombre').first()
	# 	# return cuenta


	class Meta:
		db_table = "seguimiento_factura_gestion_op"
		permissions = (("can_see_seguimiento_factura","can_see_seguimiento_factura"),
						("can_see_seguimiento_factura_por_contabilizar","can_see_seguimiento_factura_por_contabilizar"),
						("can_see_seguimiento_factura_habilitar_tes_op","can_see_seguimiento_factura_habilitar_tes_op"),
						("can_see_seguimiento_factura_test_op","can_see_seguimiento_factura_test_op"),
						("can_see_seguimiento_factura_recursos_propios","can_see_seguimiento_factura_recursos_propios"),
						("can_see_seguimiento_factura_por_pagar","can_see_seguimiento_factura_por_pagar"),
						("can_see_seguimiento_factura_consultar_pago","can_see_seguimiento_factura_consultar_pago"),
						("can_see_seguimiento_factura_administrador_cuenta","can_see_seguimiento_factura_administrador_cuenta"),
						)