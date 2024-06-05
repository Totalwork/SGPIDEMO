from django.contrib import admin
from .models import ConfiguracionPorcentajes, ProyectosNotificados, Aretie, AsistenteVisita, \
					NotificarCorreo, Historial, NoConformidad, Soporte
# Register your models here.

@admin.register(ConfiguracionPorcentajes)
class AdminConfiguracionPorcentajes(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('contrato', 'porcentaje')
	search_fields=('contrato', 'porcentaje',)

@admin.register(ProyectosNotificados)
class AdminProyectosNotificados(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('proyecto', 'enviado', 'fecha')
	search_fields=('proyecto', 'enviado',)	

@admin.register(Aretie)
class AdminRetie(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('proyecto', 'fecha_programada', 'fecha_ejecutada', 'hora', 'estado')
	search_fields=('proyecto',)	

@admin.register(AsistenteVisita)
class AdminAsistenteVisita(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('retie', 'persona', 'rol', 'no_asistio', 'notificacion_enviada')
	search_fields=('retie', 'persona', 'rol', 'no_asistio',)			

@admin.register(NotificarCorreo)
class AdminNotificarCorreo(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('retie', 'correo', 'nombre', 'notificacion_enviada')
	search_fields=('retie', 'correo', 'nombre',)				

@admin.register(Historial)
class AdminHistorial(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('retie', 'estado', 'fecha_programada', 'fecha_ejecutada', 'hora', 'usuario')
	search_fields=('retie', 'estado', )					

@admin.register(NoConformidad)
class AdminNoConformidad(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('retie', 'descripcion', 'corregida')
	search_fields=('retie', 'descripcion', )		

@admin.register(Soporte)
class AdminSoporte(admin.ModelAdmin):
	"""docstring para Escolaridad"""
	list_display=('retie', 'soporte', 'nombre')
	search_fields=('retie', 'nombre', )						

	