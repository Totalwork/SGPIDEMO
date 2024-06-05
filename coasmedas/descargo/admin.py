from django.contrib import admin
from .models import Correo_descargo,AIdInternoDescargo,ATrabajo,AManiobra,ABMotivoSgi,AMotivoInterventor,Descargo
from empresa.models import Empresa
from usuario.models import Persona
# Register your models here.
class AdminCorreo_descargo(admin.ModelAdmin):
	list_display=('nombre','apellido','correo','tipo','contratista')
	list_filter=('contratista',)
	search_fields=('nombre',)	


class AdminIdInternoDescargo(admin.ModelAdmin):
	list_display=('convenio','departamento','numero')
	list_filter=('convenio','departamento',)
	search_fields=('numero',)


class AdminATrabajo(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)

class AdminAManiobra(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)

class AdminABMotivoSgi(admin.ModelAdmin):
	list_display=('nombre','estado_descargo')
	search_fields=('nombre',)

class AdminAMotivoInterventor(admin.ModelAdmin):
	list_display=('nombre','motivo_sgi')
	search_fields=('nombre',)

class AdminDescargo(admin.ModelAdmin):
	list_display=('id_interno','numero','estado','proyecto','barrio','direccion','bdi','perdida_mercado','area_afectada','elemento_intervenir','maniobra','fecha','hora_inicio'
		,'hora_fin','jefe_trabajo','agente_descargo','observacion','correo_bdi','soporte_ops','soporte_protocolo','lista_chequeo','numero_requerimiento','contratista','motivo_sgi','motivo_interventor')
	list_filter=('estado',)
	search_fields=('id_interno',)	


admin.site.register(Correo_descargo,AdminCorreo_descargo)
admin.site.register(AIdInternoDescargo,AdminIdInternoDescargo)
admin.site.register(ATrabajo,AdminATrabajo)
admin.site.register(AManiobra,AdminAManiobra)
admin.site.register(ABMotivoSgi,AdminABMotivoSgi)
admin.site.register(AMotivoInterventor,AdminAMotivoInterventor)
admin.site.register(Descargo,AdminDescargo)
