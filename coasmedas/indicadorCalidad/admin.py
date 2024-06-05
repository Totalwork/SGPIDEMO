from django.contrib import admin
from .models import AIndicador,BSeguimientoIndicador,Periodicidad
# Register your models here.

class AdminAIndicador(admin.ModelAdmin):
	list_display=('nombre','unidadMedida','objetivoAnual')
	search_fields=('nombre',)

class AdminBSeguimientoIndicador(admin.ModelAdmin):
	list_display=('indicador','inicioPeriodo','finPeriodo','valor')
	search_fields=('indicador',)

class AdminPeriodicidad(admin.ModelAdmin):
	list_display=('dias','descripcion')
	search_fields=('dias',)	


admin.site.register(AIndicador,AdminAIndicador)
admin.site.register(BSeguimientoIndicador,AdminBSeguimientoIndicador)
admin.site.register(Periodicidad,AdminPeriodicidad)