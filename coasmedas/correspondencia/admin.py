from django.contrib import admin
from .models import CorrespondenciaEnviada, CorrespondenciaConsecutivo, CorresPfijo , CorrespondenciaSoporte , CorrespondenciaRadicado

# Register your models here.
class AdminCorrespondenciaPrefijo(admin.ModelAdmin):
	list_display=('nombre' , 'empresa' , 'estado')
	list_filter=('nombre', 'empresa')
	search_fields=('nombre',)

class AdminCorrespondenciaConsecutivo(admin.ModelAdmin):
	list_display=( 'prefijo' , 'ano' , 'numero')
	list_filter=( 'prefijo' , 'ano' )
	search_fields=('prefijo',)

class AdminCorrespondenciaEnviada(admin.ModelAdmin):
	list_display=( 'prefijo', 'consecutivo' , 'fechaEnvio' , 'asunto' , 'referencia' , 'persona_destino' , 'anulado')
	list_filter=('empresa', 'fechaEnvio' , 'anoEnvio' , 'grupoSinin' , 'anulado')
	search_fields=('consecutivo',)

class AdminCorrespondenciaSoporte(admin.ModelAdmin):
	list_display=('nombre' , 'correspondencia' , 'anulado')
	list_filter=('nombre', )
	search_fields=('nombre',)


class AdminCorrespondenciaRadicado(admin.ModelAdmin):
	list_display=( 'empresa' , 'ano' , 'numero')
	list_filter=( 'empresa' , 'ano' )
	search_fields=('empresa',)


admin.site.register(CorresPfijo, AdminCorrespondenciaPrefijo)
admin.site.register(CorrespondenciaConsecutivo, AdminCorrespondenciaConsecutivo)
admin.site.register(CorrespondenciaEnviada, AdminCorrespondenciaEnviada)
admin.site.register(CorrespondenciaSoporte, AdminCorrespondenciaSoporte)
admin.site.register(CorrespondenciaRadicado, AdminCorrespondenciaRadicado)