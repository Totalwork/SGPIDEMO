from django.contrib import admin
from control_cambios.models import ASolicita,BUnidadConstructiva,CCambio,DMaterial,EUUCCMaterial,FCambioProyecto,GSoporte
# Register your models here.
class Solicita(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)		

admin.site.register(ASolicita,Solicita)


class UnidadCounstructiva(admin.ModelAdmin):
	list_display=('codigo','descripcion','contrato','proyecto',)
	search_fields=('codigo','descripcion','contrato__nombre','proyecto__nombre',)	

admin.site.register(BUnidadConstructiva,UnidadCounstructiva)


class Cambio(admin.ModelAdmin):
	list_display=('proyecto','fecha','usuario','solicita','numero_cambio','tipo','motivo',)
	list_filter=('tipo','fecha',)
	search_fields=('numero_cambio','proyecto__nombre','motivo',)	

admin.site.register(CCambio,Cambio)


class Material(admin.ModelAdmin):
	list_display=('codigo','descripcion','unidad',)
	search_fields=('codigo','descripcion','unidad',)	

admin.site.register(DMaterial,Material)


class EuuccMaterial(admin.ModelAdmin):
	list_display=('uucc','material',)
	#search_fields=('numero_cambio','proyecto__nombre','motivo',)	

admin.site.register(EUUCCMaterial,EuuccMaterial)


class CambioProyecto(admin.ModelAdmin):
	list_display=('uucc','cambio','estado','comentario',)
	list_filter=('estado',)
	search_fields=('comentario',)	

admin.site.register(FCambioProyecto,CambioProyecto)


class soporte(admin.ModelAdmin):
	list_display=('cambio','nombre',)
	search_fields=('nombre',)	

admin.site.register(GSoporte,soporte)