from django.contrib import admin
from giros.models import CNombreGiro,DEncabezadoGiro,DetalleGiro
# Register your models here.
class AdminCNombreGiro(admin.ModelAdmin):
	list_display=('nombre','contrato','tipo',)
	search_fields=('nombre','contrato__nombre',)	

admin.site.register(CNombreGiro,AdminCNombreGiro)


class AdminDEncabezadoGiro(admin.ModelAdmin):
	list_display=('nombre','contrato','soporte','referencia','num_causacion','fecha_conta','disparar_flujo','numero_radicado',)
	list_filter=('nombre','fecha_conta',)
	search_fields=('numero_radicado','contrato__nombre',)	

admin.site.register(DEncabezadoGiro,AdminDEncabezadoGiro)


class AdminDetalleGiro(admin.ModelAdmin):
	list_display=('contratista','banco','no_cuenta','tipo_cuenta','valor_girar','carta_autorizacion','estado','fecha_pago','cuenta','test_op','fecha_pago_esperada','codigo_pago',)
	list_filter=('contratista','banco','fecha_pago',)
	search_fields=('no_cuenta',)

admin.site.register(DetalleGiro,AdminDetalleGiro)