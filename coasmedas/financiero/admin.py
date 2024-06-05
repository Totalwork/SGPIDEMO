from django.contrib import admin
from financiero.models import FinancieroCuenta,FinancieroCuentaMovimiento
# Register your models here.
class AdminFinancieroCuenta(admin.ModelAdmin):
	list_display=('numero','valor','contrato','fiduciaria','tipo','codigo_fidecomiso','codigo_fidecomiso_a','nombre_fidecomiso','empresa',)
	list_filter=('tipo',)
	search_fields=('numero','contrato__nombre','empresa__nombre',)	

admin.site.register(FinancieroCuenta,AdminFinancieroCuenta)


class AdminFinancieroCuentaMovimiento(admin.ModelAdmin):
	list_display=('cuenta','tipo','valor','descripcion','fecha','periodo_inicio','periodo_final','ano',)
	list_filter=('tipo',)
	search_fields=('descripcion','valor','cuenta__nombre',)	

admin.site.register(FinancieroCuentaMovimiento,AdminFinancieroCuentaMovimiento)