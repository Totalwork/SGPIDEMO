from django.contrib import admin
from factura.models import Factura, MesCausado, Cesion, Descuento, Compensacion, DetalleCompensacion, FacturaProyecto
# Register your models here.

class AdminFactura(admin.ModelAdmin):
	list_display=('id','referencia','numero','contrato','estado','fecha','concepto','valor_factura','valor_contable','valor_subtotal','soporte','pagada')
	list_filter=('referencia','numero','contrato','estado','concepto',)
	search_fields=('referencia','numero','concepto',)

class AdminCesion(admin.ModelAdmin):
	list_display=('id','referencia','contrato','beneficiario','fecha','descripcion','valor','banco','numero_cuenta','soporte')
	list_filter=('referencia','descripcion','contrato',)
	search_fields=('referencia','descripcion',)

class AdminDescuento(admin.ModelAdmin):
	list_display=('id','referencia','contrato','concepto','valor','banco','numero_cuenta','soporte')
	list_filter=('referencia','concepto','contrato',)
	search_fields=('referencia','concepto',)

class AdminCompensacion(admin.ModelAdmin):
	list_display=('id','referencia','contrato','fecha','descripcion','valor')
	list_filter=('referencia','descripcion','contrato',)
	search_fields=('referencia','descripcion',)

class AdminDetalleCompensacion(admin.ModelAdmin):
	list_display=('id','compensacion','tablaForanea','id_registro')
	list_filter=('compensacion','tablaForanea',)

class AdminMesCausado(admin.ModelAdmin):
	list_display=('id','factura','mes','ano')
	list_filter=('factura','mes','ano',)
	search_fields=('mes','ano',)

class AdminFacturaProyecto(admin.ModelAdmin):
	list_display=('id','factura','proyecto','valor')
	list_filter=('factura','proyecto',)
	# search_fields=('factura','proyecto',)

admin.site.register(Factura,AdminFactura)
admin.site.register(Cesion,AdminCesion)
admin.site.register(Descuento,AdminDescuento)
admin.site.register(Compensacion,AdminCompensacion)
admin.site.register(DetalleCompensacion,AdminDetalleCompensacion)
admin.site.register(MesCausado,AdminMesCausado)
admin.site.register(FacturaProyecto,AdminFacturaProyecto)