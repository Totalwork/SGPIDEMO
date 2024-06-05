from django.contrib import admin
from .models import AProceso, BItem, CPermisoEmpresaItem, DVinculo, ECampoInforme,FProcesoRelacion 
from .models import GProcesoRelacionDato, HSoporteProcesoRelacionDato, INotificacionVencimiento, JSeguidorProcesoRelacion

# Register your models here.

class AdminAProceso(admin.ModelAdmin):
	list_display=('nombre','activo','nombreApuntador','tablaReferencia',
		'campoEnlace','tablaForanea','campoEnlaceTablaForanea','etiqueta','pasoAPaso')
	search_fields=('nombre',)
	list_filter=('activo','apuntador','tablaReferencia',
		'campoEnlace','tablaForanea','campoEnlaceTablaForanea')

class AdminBItem(admin.ModelAdmin):
	list_display=('descripcion','orden','tipoDato','tieneVencimiento',
		'tieneObservacion','tieneSoporte','soporteObligatorio','activo',
		'notificacionCumplimiento','afectarImplementacionesAnteriores', 'contratistaResponsable')
	search_fields=('descripcion',)
	list_filter=('proceso','tipoDato','tieneVencimiento','tieneObservacion','tieneSoporte',
		'soporteObligatorio','notificacionCumplimiento','responsable')

class AdminCPermisoEmpresaItem(admin.ModelAdmin):
	list_display=('nombreProceso','nombreEmpresa','descripcionItem','lectura','escritura')
	search_fields=('item__descripcion',)
	list_filter=('item__proceso','empresa','lectura','escritura')

class AdminDVinculo(admin.ModelAdmin):
	list_display=('nombreProcesoOrigen','nombreProcesoDestino','descripcionItemVinculado')
	search_fields=('itemVinculado__descripcion',)
	list_filter=('procesoOrigen__nombre','procesoDestino__nombre')

class AdminECampoInforme(admin.ModelAdmin):
	list_display=('nombreProceso','nombreCampoApuntador','nombreTablaForanea','campoTablaForanea')
	search_fields=('proceso__nombre',)
	list_filter=('tablaForanea',)

class AdminFProcesoRelacion(admin.ModelAdmin):
	list_display=('nombreProceso','apuntador','idApuntador','idTablaReferencia')
	search_fields=('proceso__nombre','idApuntador','idTablaReferencia')
	list_filter=('proceso__apuntador','proceso')

class AdminGProcesoRelacionDato(admin.ModelAdmin):
	list_display=('nombreProceso','nombreItem','valor','nombreEstado')
	search_fields=('procesoRelacion__proceso__nombre','item__descripcion')
	list_filter=('estado','procesoRelacion__proceso__nombre','item__descripcion')

class AdminHSoporteProcesoRelacionDato(admin.ModelAdmin):
	list_display=('nombreProceso','nombreItem','nombre','archivo',)
	search_fields=('nombre',)
	list_filter=('procesoRelacionDato__procesoRelacion__proceso__nombre',
		'procesoRelacionDato__item__descripcion')

class AdminINotificacionVencimiento(admin.ModelAdmin):
	list_display=('procesoANotificar','elementoAnalizado','itemANotificar','empresaFuncionario',
		'funcionario','responsableTitular')
	search_fields=('funcionario__persona__nombres','funcionario__persona__apellidos')
	list_filter=('funcionario',
		'procesoRelacionDato__procesoRelacion__proceso__nombre')

class AdminJSeguidorProcesoRelacion(admin.ModelAdmin):
	list_display=('usuario','procesoRelacion')
	list_filter=('usuario',)

admin.site.register(AProceso,AdminAProceso)
admin.site.register(BItem,AdminBItem)
admin.site.register(CPermisoEmpresaItem,AdminCPermisoEmpresaItem)
admin.site.register(DVinculo,AdminDVinculo)
admin.site.register(ECampoInforme,AdminECampoInforme)
admin.site.register(FProcesoRelacion,AdminFProcesoRelacion)
admin.site.register(GProcesoRelacionDato,AdminGProcesoRelacionDato)
admin.site.register(HSoporteProcesoRelacionDato,AdminHSoporteProcesoRelacionDato)
admin.site.register(INotificacionVencimiento,AdminINotificacionVencimiento)
admin.site.register(JSeguidorProcesoRelacion,AdminJSeguidorProcesoRelacion)

