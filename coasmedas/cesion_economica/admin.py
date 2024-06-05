from django.contrib import admin
from cesion_economica.models import CesionEconomica
# Register your models here.
class Cesioneconomica(admin.ModelAdmin):
	list_display=('proveedor','contrato','tipo_cuenta','estado','banco',)
	search_fields=('numero_cuenta',)		

admin.site.register(CesionEconomica,Cesioneconomica)
