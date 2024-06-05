from django.contrib import admin
from .models import AArea, BSolicitud, CSoportesSolicitud
# Register your models here.

class AdminArea(admin.ModelAdmin):
	list_display=('nombre','responsable')
	search_fields=('nombre',)

class AdminSolicitudServicio(admin.ModelAdmin):
	list_display = ('estado','descripcion','fechaCreacion','area','nombreSolicitante',
		'tipo','numeroContrato')
	list_filter = ('tipo',)
	search_fields=('descripcion','numeroContrato',)

class AdminSoporteSolicitud(admin.ModelAdmin):
	list_display = ('solicitud','fechaCreacion', 'nombre','archivo')
	ist_filter=('solicitud',)
	search_fields=('nombre',)


admin.site.register(AArea,AdminArea)
admin.site.register(BSolicitud,AdminSolicitudServicio)
admin.site.register(CSoportesSolicitud,AdminSoporteSolicitud)