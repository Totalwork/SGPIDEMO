from django.contrib import admin
from cesion_v2.models import CesionV, DetalleCesionV

#Register your models here.
class Cesionv2(admin.ModelAdmin):
	list_display=('contratista','fecha_carta','estado',)	

admin.site.register(CesionV,Cesionv2)


class DetallecesionV(admin.ModelAdmin):
	list_display=('cesion','contrato','nombre_giro','beneficiario','banco','tipo_cuenta','estado','numero_cuenta','valor',)
	search_fields=('numero_cuenta',)	

admin.site.register(DetalleCesionV,DetallecesionV)
