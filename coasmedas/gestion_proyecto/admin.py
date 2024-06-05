from django.contrib import admin
from .models import AFondo,ACampana,ASolicitante,AUnidadMedida,CampanaEmpresa,CSolicitud,DatoDiseno,Diseno,SoporteSolicitud
from .models import DocumentoEstado,EstadoDiseno,InfoDiseno,MapaDiseno,PermisoDiseno,SoporteEstado,SoporteEstadoComentario

# Register your models here.
class AdminFondo(admin.ModelAdmin):
	list_display=('nombre','empresa','estado',)
	search_fields=('nombre','empresa',)
	list_filter=('nombre','empresa',)		

admin.site.register(AFondo,AdminFondo)

class AdminCampana(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)
	list_filter=('nombre',)		

admin.site.register(ACampana,AdminCampana)

class AdminSolicitante(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)
	list_filter=('nombre',)		

admin.site.register(ASolicitante,AdminSolicitante)

class AdminUnidadMedida(admin.ModelAdmin):
	list_display=('nombre',)
	search_fields=('nombre',)
	list_filter=('nombre',)		

admin.site.register(AUnidadMedida,AdminUnidadMedida)

class AdminCampanaEmpresa(admin.ModelAdmin):
	list_display=('campana','empresa','propietario',)
	search_fields=('campana','empresa','propietario',)
	list_filter=('campana','empresa','propietario',)		

admin.site.register(CampanaEmpresa,AdminCampanaEmpresa)

class AdminSolicitud(admin.ModelAdmin):
	list_display=('entidad','visita','descripcion_visita','fecha','fecha_visita','fecha_respuesta',)
	search_fields=('entidad','visita',)
	list_filter=('entidad','visita',)		

admin.site.register(CSolicitud,AdminSolicitud)

class AdminDatoDiseno(admin.ModelAdmin):
	list_display=('nombre','unidad_medida','orden',)
	search_fields=('nombre','unidad_medida','orden',)
	list_filter=('nombre','unidad_medida','orden',)		

admin.site.register(DatoDiseno,AdminDatoDiseno)

class AdminDiseno(admin.ModelAdmin):
	list_display=('fondo','solicitante','campana','municipio','propietaria','activado','costo_proyecto','costo_diseno',)
	search_fields=('fondo','solicitante','campana','propietaria',)
	list_filter=('fondo','solicitante','campana','propietaria',)		

admin.site.register(Diseno,AdminDiseno)

class AdminDocumentoEstado(admin.ModelAdmin):
	list_display=('nombre','estado','campana',)
	search_fields=('nombre','estado','campana',)
	list_filter=('nombre','estado','campana',)		

admin.site.register(DocumentoEstado,AdminDocumentoEstado)

class AdminEstadoDiseno(admin.ModelAdmin):
	list_display=('diseno','estado','fecha',)
	search_fields=('diseno','estado',)
	list_filter=('diseno','estado',)		

admin.site.register(EstadoDiseno,AdminEstadoDiseno)

class AdminInfoDiseno(admin.ModelAdmin):
	list_display=('diseno','dato_diseno','valor',)
	search_fields=('diseno','dato_diseno',)
	list_filter=('diseno','dato_diseno',)		

admin.site.register(InfoDiseno,AdminInfoDiseno)

class AdminMapaDiseno(admin.ModelAdmin):
	list_display=('diseno','longitud','latitud','nombre',)
	search_fields=('diseno',)
	list_filter=('diseno',)		

admin.site.register(MapaDiseno,AdminMapaDiseno)

class AdminPermisoDiseno(admin.ModelAdmin):
	list_display=('diseno','empresa','consultar','editar',)
	search_fields=('diseno','empresa',)
	list_filter=('diseno','empresa',)		

admin.site.register(PermisoDiseno,AdminPermisoDiseno)

class AdminSoporteEstado(admin.ModelAdmin):
	list_display=('estado_diseno','documento_estado','fecha','ruta','usuario',)
	search_fields=('estado_diseno','documento_estado','usuario',)
	list_filter=('estado_diseno','documento_estado','usuario',)		

admin.site.register(SoporteEstado,AdminSoporteEstado)

class AdminSoporteEstadoComentario(admin.ModelAdmin):
	list_display=('soporte_estado','fecha','comentario','usuario',)
	search_fields=('soporte_estado','usuario',)
	list_filter=('soporte_estado','usuario',)		

admin.site.register(SoporteEstadoComentario,AdminSoporteEstadoComentario)

class AdminSoporteSolicitud(admin.ModelAdmin):
	list_display=('solicitud','fecha','ruta','usuario',)
	search_fields=('solicitud','usuario',)
	list_filter=('solicitud','usuario',)		

admin.site.register(SoporteSolicitud,AdminSoporteSolicitud)