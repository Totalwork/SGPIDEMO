from django.contrib import admin
from .models import SolicitudConsecutivo, ConjuntoEvento, Evento , Solicitud , SolicitudSoporte , SolicitudEmpresa , SolicitudEvento , SolicitudHistorial , SolicitudApelacion , SolicitudPronunciamiento

# Register your models here.
class AdminSolicitudConsecutivo(admin.ModelAdmin):
	list_display=('consecutivo' , 'empresa')
	list_filter=('consecutivo', 'empresa')
	search_fields=('consecutivo',)

class AdminConjuntoEvento(admin.ModelAdmin):
	list_display=('id' , 'nombre')
	list_filter=('nombre', )
	search_fields=('nombre',)

class AdminEvento(admin.ModelAdmin):
	list_display=('id' , 'nombre' , 'valor' , 'conjunto')
	list_filter=('conjunto', )
	search_fields=('nombre',)

class AdminSolicitud(admin.ModelAdmin):
	list_display=('consecutivo' , 'contrato' , 'correspondenciasolicita' , 'firmaImposicion' , 'valorSolicitado' ,'valorImpuesto')
	list_filter=('contrato',)
	search_fields=('consecutivo',)

class AdminSolicitudSoporte(admin.ModelAdmin):
	list_display=('nombre' , 'solicitud' , 'anulado')
	list_filter=('anulado', 'solicitud')
	search_fields=('nombre',)

class AdminSolicitudEmpresa(admin.ModelAdmin):
	list_display=('empresa' , 'solicitud' , 'propietario')
	list_filter=('propietario', 'empresa')
	search_fields=('empresa',)

class AdminSolicitudEvento(admin.ModelAdmin):
	list_display=('evento' , 'solicitud' , 'numeroimcumplimiento')
	list_filter=('evento', 'solicitud')
	search_fields=('evento',)

class AdminSolicitudHistorial(admin.ModelAdmin):
	list_display=('fecha' , 'solicitud' , 'estado' , 'usuario' , 'comentarios')
	list_filter=('estado', 'solicitud')
	search_fields=('estado',)

class AdminSolicitudApelacion(admin.ModelAdmin):
	list_display=('fecha' , 'solicitud' , 'comentarios')
	list_filter=('solicitud',)
	search_fields=('solicitud',)

class AdminSolicitudPronunciamiento(admin.ModelAdmin):
	list_display=('apelacion' , 'comentarios' , 'fecha_transacion')
	list_filter=('apelacion', )
	search_fields=('apelacion',)

admin.site.register(SolicitudConsecutivo, AdminSolicitudConsecutivo)
admin.site.register(ConjuntoEvento, AdminConjuntoEvento)
admin.site.register(Evento, AdminEvento)
admin.site.register(Solicitud, AdminSolicitud)
admin.site.register(SolicitudSoporte, AdminSolicitudSoporte)
admin.site.register(SolicitudEmpresa, AdminSolicitudEmpresa)
admin.site.register(SolicitudEvento, AdminSolicitudEvento)
admin.site.register(SolicitudHistorial, AdminSolicitudHistorial)
admin.site.register(SolicitudApelacion, AdminSolicitudApelacion)
admin.site.register(SolicitudPronunciamiento, AdminSolicitudPronunciamiento)
