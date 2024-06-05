from django.contrib import admin
from .models import Aseguradora, Poliza, VigenciaPoliza, ZBeneficiorio


class AdminAseguradora(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('id','nombre')
	search_fields=('nombre',)

class AdminBeneficiorio(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('nombre', 'vigencia_id')
	search_fields=('nombre',)

	def vigencia_id(self, obj):
		return obj.vigencia_poliza.id

class AdminPoliza(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('nombre_tipo','nombre_contrato',)
	search_fields=('tipo__nombre','contrato__nombre',)	

	def nombre_tipo(self, obj):
			return obj.tipo.nombre

	def nombre_contrato(self, obj):
			return obj.contrato.nombre	

class AdminVigenciaPoliza(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('numero','poliza_id','tipo_poliza','fecha_inicio', 'fecha_final', 'valor', 'aseguradora','reemplaza',)
	search_fields=('numero','fecha_inicio', 'fecha_final', 'valor', 'aseguradora__nombre')

	def poliza_id(self, obj):
		return obj.poliza.id

	def tipo_poliza(self, obj):
		return obj.poliza.tipo.nombre	

admin.site.register(Aseguradora, AdminAseguradora)
admin.site.register(Poliza, AdminPoliza)
admin.site.register(VigenciaPoliza, AdminVigenciaPoliza)
admin.site.register(ZBeneficiorio, AdminBeneficiorio)			