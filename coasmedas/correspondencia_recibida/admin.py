from django.contrib import admin
from .models import  CorrespondenciaRecibida, CorrespondenciaRecibidaAsignada , CorrespondenciaRecibidaSoporte

# Register your models here.

class AdminCorrespondenciaRecibida(admin.ModelAdmin):
	list_display=('empresa' , 'radicado' , 'fechaRecibida' , 'asunto' , 'remitente' , 'usuarioSolicitante')
	list_filter=('empresa', 'fechaRecibida' , 'anoRecibida' )
	search_fields=('nombre',)

class AdminCorrespondenciaRecibidaAsignada(admin.ModelAdmin):
	list_display=('correspondenciaRecibida' , 'usuario' , 'fechaAsignacion' , 'estado' , 'respuesta' , 'copia')
	list_filter=('usuario', 'fechaAsignacion' , 'estado' )
	# search_fields=('nombre',)

class AdminCorrespondenciaRecibidaSoporte(admin.ModelAdmin):
	list_display=('nombre' , 'correspondencia' , 'anulado')
	list_filter=('nombre', )
	search_fields=('nombre',)


admin.site.register(CorrespondenciaRecibida, AdminCorrespondenciaRecibida)	
admin.site.register(CorrespondenciaRecibidaAsignada, AdminCorrespondenciaRecibidaAsignada)
admin.site.register(CorrespondenciaRecibidaSoporte, AdminCorrespondenciaRecibidaSoporte)
